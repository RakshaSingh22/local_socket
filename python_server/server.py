import socket
import threading
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time

# Configuration
SOCKET_PATH = '/tmp/python_server.sock'
LOG_LEVEL = logging.INFO
MAX_MESSAGE_SIZE = 4096  # 4KB max message size

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# In-memory storage (can be replaced with database in production)
storage: Dict[str, Any] = {}


class ServerError(Exception):
    """Custom exception for server errors"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


def create_response(request_id: Optional[str], success: bool, data: Any = None, 
                   error: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Create a standardized response message"""
    response = {
        "type": "response",
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if request_id:
        response["request_id"] = request_id
    
    if success and data is not None:
        response["data"] = data
    elif not success and error:
        response["error"] = error
    
    return response


def create_error_response(request_id: Optional[str], error_code: str, 
                         error_message: str) -> Dict[str, Any]:
    """Create an error response"""
    return create_response(
        request_id=request_id,
        success=False,
        error={"code": error_code, "message": error_message}
    )


def handle_echo(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Echo command - returns the message sent"""
    message = command_data.get("message", "")
    if not message:
        raise ServerError("INVALID_INPUT", "Message field is required")
    return {"echo": message}


def handle_time(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Time command - returns current server time"""
    return {
        "timestamp": datetime.now().isoformat(),
        "unix_timestamp": time.time(),
        "formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def handle_calculate(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculator command - performs basic arithmetic"""
    operation = command_data.get("operation")
    a = command_data.get("a")
    b = command_data.get("b")
    
    if operation is None or a is None or b is None:
        raise ServerError("INVALID_INPUT", "operation, a, and b are required")
    
    try:
        a, b = float(a), float(b)
    except (ValueError, TypeError):
        raise ServerError("INVALID_INPUT", "a and b must be numbers")
    
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else None,
        "power": lambda x, y: x ** y,
        "modulo": lambda x, y: x % y if y != 0 else None
    }
    
    if operation not in operations:
        raise ServerError("INVALID_OPERATION", 
                         f"Operation must be one of: {', '.join(operations.keys())}")
    
    result = operations[operation](a, b)
    if result is None:
        raise ServerError("MATH_ERROR", "Division by zero or invalid operation")
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    }


def handle_store(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store command - stores key-value pairs in memory"""
    key = command_data.get("key")
    value = command_data.get("value")
    
    if key is None:
        raise ServerError("INVALID_INPUT", "key is required")
    
    storage[key] = value
    return {
        "key": key,
        "stored": True,
        "message": f"Value stored for key '{key}'"
    }


def handle_retrieve(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve command - retrieves value by key"""
    key = command_data.get("key")
    
    if key is None:
        raise ServerError("INVALID_INPUT", "key is required")
    
    if key not in storage:
        raise ServerError("KEY_NOT_FOUND", f"Key '{key}' not found in storage")
    
    return {
        "key": key,
        "value": storage[key]
    }


def handle_list_keys(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """List all stored keys"""
    return {
        "keys": list(storage.keys()),
        "count": len(storage)
    }


def handle_delete(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Delete command - removes a key from storage"""
    key = command_data.get("key")
    
    if key is None:
        raise ServerError("INVALID_INPUT", "key is required")
    
    if key not in storage:
        raise ServerError("KEY_NOT_FOUND", f"Key '{key}' not found")
    
    del storage[key]
    return {
        "key": key,
        "deleted": True,
        "message": f"Key '{key}' deleted"
    }


def handle_ping(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ping command - health check"""
    return {
        "status": "ok",
        "server_time": datetime.now().isoformat(),
        "storage_size": len(storage)
    }


def handle_help(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Help command - returns available commands"""
    return {
        "commands": {
            "echo": {
                "description": "Echo back a message",
                "parameters": {"message": "string - message to echo"}
            },
            "time": {
                "description": "Get current server time",
                "parameters": {}
            },
            "calculate": {
                "description": "Perform arithmetic operations",
                "parameters": {
                    "operation": "string - add, subtract, multiply, divide, power, modulo",
                    "a": "number - first operand",
                    "b": "number - second operand"
                }
            },
            "store": {
                "description": "Store a key-value pair",
                "parameters": {"key": "string - storage key", "value": "any - value to store"}
            },
            "retrieve": {
                "description": "Retrieve a value by key",
                "parameters": {"key": "string - storage key"}
            },
            "list_keys": {
                "description": "List all stored keys",
                "parameters": {}
            },
            "delete": {
                "description": "Delete a key from storage",
                "parameters": {"key": "string - storage key"}
            },
            "ping": {
                "description": "Health check - returns server status",
                "parameters": {}
            },
            "help": {
                "description": "Show this help message",
                "parameters": {}
            }
        }
    }


# Command handler registry
COMMAND_HANDLERS: Dict[str, callable] = {
    "echo": handle_echo,
    "time": handle_time,
    "calculate": handle_calculate,
    "store": handle_store,
    "retrieve": handle_retrieve,
    "list_keys": handle_list_keys,
    "delete": handle_delete,
    "ping": handle_ping,
    "help": handle_help
}


def process_command(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process a command and return response"""
    request_id = message.get("request_id")
    command = message.get("command")
    command_data = message.get("data", {})
    
    if not command:
        raise ServerError("INVALID_REQUEST", "Command field is required")
    
    if command not in COMMAND_HANDLERS:
        raise ServerError("UNKNOWN_COMMAND", 
                         f"Unknown command: {command}. Use 'help' to see available commands")
    
    try:
        handler = COMMAND_HANDLERS[command]
        result = handler(command_data)
        return create_response(request_id=request_id, success=True, data=result)
    except ServerError as e:
        return create_error_response(request_id=request_id, 
                                    error_code=e.code, 
                                    error_message=e.message)
    except Exception as e:
        logger.exception(f"Unexpected error processing command {command}")
        return create_error_response(request_id=request_id,
                                    error_code="INTERNAL_ERROR",
                                    error_message=f"Internal server error: {str(e)}")


def handle_client(conn, addr):
    """Handle client connection"""
    client_id = f"{addr}"
    logger.info(f"Client connected: {client_id}")
    
    try:
        # Send welcome message
        welcome = create_response(
            request_id=None,
            success=True,
            data={
                "message": "Connected to server",
                "server_time": datetime.now().isoformat(),
                "available_commands": list(COMMAND_HANDLERS.keys())
            }
        )
        conn.send((json.dumps(welcome) + '\n').encode('utf-8'))
        
        buffer = ""
        while True:
            data = conn.recv(MAX_MESSAGE_SIZE)
            if not data:
                break
            
            buffer += data.decode('utf-8')
            
            # Process complete messages (ending with newline)
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if not line:
                    continue
                
                try:
                    # Parse JSON message
                    message = json.loads(line)
                    logger.debug(f"Received from {client_id}: {message}")
                    
                    # Process command
                    response = process_command(message)
                    logger.debug(f"Sending to {client_id}: {response}")
                    
                    # Send response
                    conn.send((json.dumps(response) + '\n').encode('utf-8'))
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from {client_id}: {line}")
                    error_response = create_error_response(
                        request_id=None,
                        error_code="INVALID_JSON",
                        error_message=f"Invalid JSON format: {str(e)}"
                    )
                    conn.send((json.dumps(error_response) + '\n').encode('utf-8'))
                except Exception as e:
                    logger.exception(f"Error handling message from {client_id}")
                    error_response = create_error_response(
                        request_id=None,
                        error_code="PROCESSING_ERROR",
                        error_message=f"Error processing message: {str(e)}"
                    )
                    conn.send((json.dumps(error_response) + '\n').encode('utf-8'))
                    
    except ConnectionResetError:
        logger.info(f"Client {client_id} disconnected (connection reset)")
    except Exception as e:
        logger.exception(f"Error with client {client_id}")
    finally:
        conn.close()
        logger.info(f"Client {client_id} disconnected")


def start_server():
    """Start the server"""
    # Remove socket file if it exists
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)  # Allow up to 5 pending connections
    
    # Set socket permissions (readable/writable by user and group)
    os.chmod(SOCKET_PATH, 0o660)
    
    logger.info(f"Server started on socket: {SOCKET_PATH}")
    logger.info(f"Available commands: {', '.join(COMMAND_HANDLERS.keys())}")
    logger.info("Waiting for clients...\n")
    
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        logger.info("Server stopped")


if __name__ == "__main__":
    start_server()
