import socket
import threading
import os
import json

SOCKET_PATH = '/tmp/python_server.sock'

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
            
            # Try to parse JSON data
            try:
                json_data = json.loads(data)
                print(f"\n{'='*50}")
                print("Received JSON data:")
                print(f"  Name: {json_data.get('name', 'N/A')}")
                print(f"  Email: {json_data.get('email', 'N/A')}")
                print(f"  Full JSON: {json.dumps(json_data, indent=2)}")
                print(f"{'='*50}\n")
                
                # Send response back
                response = "message received"
                conn.send(response.encode('utf-8') + b'\n')
                print(f"Sent response: {response}")
                
            except json.JSONDecodeError:
                # Handle non-JSON data (for backward compatibility)
                print(f"Received (non-JSON): {data}")
                response = "message received"
                conn.send(response.encode('utf-8') + b'\n')
                print(f"Sent response: {response}")
                
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print(f"Client {addr} disconnected (connection closed normally)\n")
        conn.close()

def start_server():
    # Remove socket file if it exists
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen()
    print(f"Python server running on local socket: {SOCKET_PATH}")
    print("Waiting for clients...\n")
    
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)

if __name__ == "__main__":
    start_server()
