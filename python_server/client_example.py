#!/usr/bin/env python3
"""
Example client demonstrating how to interact with the production-level server.
This shows how to send commands and receive responses.
"""

import socket
import json
import uuid
from typing import Dict, Any, Optional

SOCKET_PATH = '/tmp/python_server.sock'


class SocketClient:
    """Client for communicating with the socket server"""
    
    def __init__(self, socket_path: str = SOCKET_PATH):
        self.socket_path = socket_path
        self.conn = None
    
    def connect(self):
        """Connect to the server"""
        self.conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.conn.connect(self.socket_path)
        # Read welcome message
        response = self._receive_response()
        print(f"Server welcome: {response.get('data', {}).get('message', 'Connected')}")
        return response
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _send_command(self, command: str, data: Dict[str, Any] = None, 
                     request_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a command to the server"""
        if not self.conn:
            raise ConnectionError("Not connected to server")
        
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        message = {
            "command": command,
            "request_id": request_id,
            "data": data or {}
        }
        
        self.conn.send((json.dumps(message) + '\n').encode('utf-8'))
        return self._receive_response()
    
    def _receive_response(self) -> Dict[str, Any]:
        """Receive a response from the server"""
        buffer = ""
        while True:
            data = self.conn.recv(4096).decode('utf-8')
            if not data:
                raise ConnectionError("Connection closed by server")
            
            buffer += data
            if '\n' in buffer:
                line, _ = buffer.split('\n', 1)
                return json.loads(line.strip())
    
    def echo(self, message: str) -> Dict[str, Any]:
        """Echo a message"""
        return self._send_command("echo", {"message": message})
    
    def get_time(self) -> Dict[str, Any]:
        """Get server time"""
        return self._send_command("time")
    
    def calculate(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """Perform a calculation"""
        return self._send_command("calculate", {
            "operation": operation,
            "a": a,
            "b": b
        })
    
    def store(self, key: str, value: Any) -> Dict[str, Any]:
        """Store a key-value pair"""
        return self._send_command("store", {"key": key, "value": value})
    
    def retrieve(self, key: str) -> Dict[str, Any]:
        """Retrieve a value by key"""
        return self._send_command("retrieve", {"key": key})
    
    def list_keys(self) -> Dict[str, Any]:
        """List all stored keys"""
        return self._send_command("list_keys")
    
    def delete(self, key: str) -> Dict[str, Any]:
        """Delete a key"""
        return self._send_command("delete", {"key": key})
    
    def ping(self) -> Dict[str, Any]:
        """Health check"""
        return self._send_command("ping")
    
    def help(self) -> Dict[str, Any]:
        """Get help"""
        return self._send_command("help")


def main():
    """Example usage"""
    client = SocketClient()
    
    try:
        # Connect
        print("Connecting to server...")
        client.connect()
        print()
        
        # Example 1: Echo
        print("=== Example 1: Echo ===")
        response = client.echo("Hello, Server!")
        if response.get("success"):
            print(f"Echo result: {response['data']['echo']}")
        print()
        
        # Example 2: Get time
        print("=== Example 2: Get Server Time ===")
        response = client.get_time()
        if response.get("success"):
            print(f"Server time: {response['data']['formatted']}")
        print()
        
        # Example 3: Calculator
        print("=== Example 3: Calculator ===")
        response = client.calculate("add", 10, 5)
        if response.get("success"):
            data = response['data']
            print(f"{data['a']} + {data['b']} = {data['result']}")
        
        response = client.calculate("multiply", 7, 8)
        if response.get("success"):
            data = response['data']
            print(f"{data['a']} × {data['b']} = {data['result']}")
        print()
        
        # Example 4: Storage operations
        print("=== Example 4: Storage Operations ===")
        client.store("name", "John Doe")
        client.store("age", 30)
        client.store("city", "New York")
        
        response = client.list_keys()
        if response.get("success"):
            print(f"Stored keys: {response['data']['keys']}")
        
        response = client.retrieve("name")
        if response.get("success"):
            print(f"Retrieved name: {response['data']['value']}")
        
        client.delete("age")
        response = client.list_keys()
        if response.get("success"):
            print(f"Keys after deletion: {response['data']['keys']}")
        print()
        
        # Example 5: Error handling
        print("=== Example 5: Error Handling ===")
        response = client.retrieve("nonexistent_key")
        if not response.get("success"):
            error = response.get("error", {})
            print(f"Error: {error.get('code')} - {error.get('message')}")
        print()
        
        # Example 6: Help
        print("=== Example 6: Help ===")
        response = client.help()
        if response.get("success"):
            commands = response['data']['commands']
            print(f"Available commands: {', '.join(commands.keys())}")
        print()
        
        # Example 7: Ping
        print("=== Example 7: Ping (Health Check) ===")
        response = client.ping()
        if response.get("success"):
            print(f"Server status: {response['data']['status']}")
            print(f"Storage size: {response['data']['storage_size']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("\nDisconnected from server")


if __name__ == "__main__":
    main()

