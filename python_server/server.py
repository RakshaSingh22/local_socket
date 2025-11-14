import socket
import threading
import os

SOCKET_PATH = '/tmp/python_server.sock'

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    
    try:
        # Send "hello" when client connects
        conn.send(b'hello\n')
        print(f"Sent: hello")
        
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
            
            print(f"Received: {data}")
            
            # If client sends "hi", respond with "hello"
            if data == "hi":
                conn.send(b'hello\n')
                print(f"Sent: hello")
            elif data == "hello":
                conn.send(b'hi\n')
                print(f"Sent: hi")
                
    except Exception as e:
        print(f"Client {addr} disconnected")
    finally:
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
