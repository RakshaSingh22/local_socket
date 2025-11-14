# Production-Level Socket Server API Documentation

## Overview

This is a production-ready socket server that uses JSON-based messaging protocol over Unix domain sockets. It provides multiple useful commands for real-world applications.

## Connection

**Socket Path:** `/tmp/python_server.sock`

The server uses Unix domain sockets for local communication. Clients connect to this socket file.

## Message Protocol

All messages are JSON objects sent as text with newline (`\n`) termination.

### Request Format

```json
{
  "command": "command_name",
  "request_id": "optional-unique-id",
  "data": {
    "parameter1": "value1",
    "parameter2": "value2"
  }
}
```

### Response Format

**Success Response:**
```json
{
  "type": "response",
  "success": true,
  "request_id": "optional-unique-id",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "result": "data here"
  }
}
```

**Error Response:**
```json
{
  "type": "response",
  "success": false,
  "request_id": "optional-unique-id",
  "timestamp": "2024-01-01T12:00:00",
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Available Commands

### 1. `echo`

Echo back a message.

**Request:**
```json
{
  "command": "echo",
  "data": {
    "message": "Hello, World!"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "echo": "Hello, World!"
  }
}
```

---

### 2. `time`

Get current server time.

**Request:**
```json
{
  "command": "time",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-01T12:00:00.123456",
    "unix_timestamp": 1704110400.123456,
    "formatted": "2024-01-01 12:00:00"
  }
}
```

---

### 3. `calculate`

Perform arithmetic operations.

**Operations:** `add`, `subtract`, `multiply`, `divide`, `power`, `modulo`

**Request:**
```json
{
  "command": "calculate",
  "data": {
    "operation": "add",
    "a": 10,
    "b": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "operation": "add",
    "a": 10,
    "b": 5,
    "result": 15
  }
}
```

**Error Example (division by zero):**
```json
{
  "success": false,
  "error": {
    "code": "MATH_ERROR",
    "message": "Division by zero or invalid operation"
  }
}
```

---

### 4. `store`

Store a key-value pair in server memory.

**Request:**
```json
{
  "command": "store",
  "data": {
    "key": "username",
    "value": "john_doe"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "key": "username",
    "stored": true,
    "message": "Value stored for key 'username'"
  }
}
```

---

### 5. `retrieve`

Retrieve a value by key.

**Request:**
```json
{
  "command": "retrieve",
  "data": {
    "key": "username"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "key": "username",
    "value": "john_doe"
  }
}
```

**Error Response (key not found):**
```json
{
  "success": false,
  "error": {
    "code": "KEY_NOT_FOUND",
    "message": "Key 'username' not found in storage"
  }
}
```

---

### 6. `list_keys`

List all stored keys.

**Request:**
```json
{
  "command": "list_keys",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "keys": ["username", "age", "city"],
    "count": 3
  }
}
```

---

### 7. `delete`

Delete a key from storage.

**Request:**
```json
{
  "command": "delete",
  "data": {
    "key": "username"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "key": "username",
    "deleted": true,
    "message": "Key 'username' deleted"
  }
}
```

---

### 8. `ping`

Health check - returns server status.

**Request:**
```json
{
  "command": "ping",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "server_time": "2024-01-01T12:00:00",
    "storage_size": 5
  }
}
```

---

### 9. `help`

Get help about available commands.

**Request:**
```json
{
  "command": "help",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "commands": {
      "echo": {
        "description": "Echo back a message",
        "parameters": {"message": "string - message to echo"}
      },
      ...
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request is missing required fields |
| `INVALID_JSON` | Message is not valid JSON |
| `UNKNOWN_COMMAND` | Command does not exist |
| `INVALID_INPUT` | Missing or invalid input parameters |
| `INVALID_OPERATION` | Invalid operation for calculate command |
| `MATH_ERROR` | Mathematical error (e.g., division by zero) |
| `KEY_NOT_FOUND` | Key not found in storage |
| `PROCESSING_ERROR` | Error processing the request |
| `INTERNAL_ERROR` | Internal server error |

## Usage Examples

### Python Client

See `client_example.py` for a complete Python client implementation.

### JavaScript/Node.js Client

```javascript
const net = require('net');
const SOCKET_PATH = '/tmp/python_server.sock';

const client = net.createConnection(SOCKET_PATH, () => {
  // Send echo command
  const message = {
    command: 'echo',
    request_id: '123',
    data: { message: 'Hello, Server!' }
  };
  client.write(JSON.stringify(message) + '\n');
});

client.on('data', (data) => {
  const response = JSON.parse(data.toString().trim());
  console.log('Response:', response);
  client.end();
});
```

### cURL-like Testing

You can use `socat` or `nc` to test the server:

```bash
# Using socat
echo '{"command":"ping","data":{}}' | socat - UNIX-CONNECT:/tmp/python_server.sock

# Using netcat (if available)
echo '{"command":"time","data":{}}' | nc -U /tmp/python_server.sock
```

## Production Features

✅ **JSON Protocol** - Structured, parseable messages  
✅ **Error Handling** - Comprehensive error codes and messages  
✅ **Request Tracking** - Optional request IDs for correlation  
✅ **Logging** - Detailed logging for debugging  
✅ **Multiple Commands** - Useful operations for real applications  
✅ **Thread Safety** - Handles multiple concurrent clients  
✅ **Graceful Shutdown** - Clean resource cleanup  
✅ **Input Validation** - Validates all inputs  
✅ **Message Size Limits** - Prevents memory issues  

## Extending the Server

To add new commands:

1. Create a handler function:
```python
def handle_my_command(command_data: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    return {"result": "data"}
```

2. Register it in `COMMAND_HANDLERS`:
```python
COMMAND_HANDLERS["my_command"] = handle_my_command
```

That's it! The server will automatically handle routing and error handling.

