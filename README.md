# Socket Communication: Python Server with Electron & Flutter Clients

Simple socket-based communication examples using **Unix domain sockets** (local sockets) for seamless communication between Python, Electron, and Flutter on the same machine.

## Project Structure

```
Socket/
├── python_server/     # Python server using Unix domain socket
├── electron_client/   # Electron client using Unix domain socket
└── flutter_client/    # Flutter client using Unix domain socket
```

---

## Why Unix Domain Sockets?

**Unix domain sockets** (also called local sockets) provide several advantages over TCP/IP sockets:

- ✅ **No IP Address Issues**: No need to configure IP addresses or worry about network settings
- ✅ **Faster**: Direct kernel-level communication, no network stack overhead
- ✅ **More Secure**: Only accessible from the same machine
- ✅ **Simpler**: Just a file path, no ports or IPs to manage
- ✅ **No Firewall Issues**: Not affected by firewall rules

**Socket File Location:** `/tmp/python_server.sock`

---

## 1. Electron ↔ Python Connection

### How It Works

Electron and Python connect using a Unix domain socket file. Both run on the same machine and communicate through a local socket file.

**Connection Flow:**
1. Python server creates a Unix socket at `/tmp/python_server.sock`
2. Electron client connects to the same socket file
3. Both exchange "hello" and "hi" messages

### Why It's Simple

- **Same Machine**: Both Electron and Python run on your computer
- **Local Socket**: Uses a file path instead of IP/port
- **No Network Configuration**: No IP addresses, ports, or firewall rules needed
- **Native Support**: Node.js `net` module supports Unix sockets directly

### Running Electron + Python

**Terminal 1 - Start Python Server:**
```bash
cd python_server
python server.py
```

You should see:
```
Python server running on local socket: /tmp/python_server.sock
Waiting for clients...
```

**Terminal 2 - Start Electron Client:**
```bash
cd electron_client
npm start
```

**Output:**
- **Python Terminal**: Shows "Client connected" and message exchange
- **Electron Terminal**: Shows connection status and message exchange

---

## 2. Flutter ↔ Python Connection

### How It Works

Flutter connects to Python using the same Unix domain socket. Dart's `RawSocket` class provides access to Unix domain sockets on Unix-like systems (macOS, Linux).

**Connection Flow:**
1. Python server creates a Unix socket at `/tmp/python_server.sock`
2. Flutter client connects to the same socket file
3. Both exchange "hello" and "hi" messages

### Platform Support

#### **macOS / Linux Desktop** ✅
- ✅ Full Unix socket support
- ✅ Works out of the box
- ✅ No IP configuration needed

#### **iOS Simulator** ✅
- ✅ Unix sockets work on iOS simulator
- ✅ Same machine, same file system access

#### **Android Emulator** ⚠️
- ⚠️ Limited Unix socket support
- ⚠️ May need TCP fallback for Android

#### **Physical Android/iOS Device** ❌
- ❌ Cannot access host machine's file system
- ❌ Unix sockets won't work
- ⚠️ **Solution**: Use TCP/IP with your computer's local IP address

### Running Flutter + Python

**Terminal 1 - Start Python Server:**
```bash
cd python_server
python server.py
```

**Terminal 2 - Start Flutter Client:**
```bash
cd flutter_client
flutter run
```

**For macOS/iOS Simulator:**
```bash
flutter run -d macos
# or
flutter run -d ios
```

**Output:**
- **Python Terminal**: Shows "Client connected" and message exchange
- **Flutter Terminal**: Shows connection status and message exchange

---

## Message Exchange Protocol

Both clients follow the same simple protocol:

1. **Server sends "hello"** when client connects
2. **Client receives "hello"** → responds with "hi"
3. **Server receives "hi"** → responds with "hello"
4. **Client receives "hello"** → responds with "hi"
5. This continues back and forth...

All messages are sent as plain text with newline (`\n`) termination.

---

## Troubleshooting

### Socket File Already Exists
If you see an error about the socket file existing:
```bash
rm /tmp/python_server.sock
```

The server automatically removes the socket file on startup, but if it crashes, you may need to remove it manually.

### Permission Issues
Make sure the socket file has proper permissions:
```bash
ls -l /tmp/python_server.sock
```

### Flutter on Physical Devices
For physical Android/iOS devices, Unix sockets won't work. You'll need to:
1. Switch back to TCP/IP sockets
2. Use your computer's local IP address
3. Ensure both devices are on the same Wi-Fi network

---

## Summary

| Client | Platform | Socket Type | Complexity |
|--------|----------|-------------|------------|
| **Electron** | Desktop | Unix Domain Socket | ✅ Simple |
| **Flutter** | macOS Desktop | Unix Domain Socket | ✅ Simple |
| **Flutter** | iOS Simulator | Unix Domain Socket | ✅ Simple |
| **Flutter** | Android Emulator | Unix Domain Socket | ⚠️ May need TCP |
| **Flutter** | Physical Device | TCP/IP Required | ⚠️ Needs IP config |

**Key Takeaway:** Unix domain sockets eliminate IP address configuration issues for local development. They work perfectly for Electron and Flutter on desktop/simulator, but physical mobile devices require TCP/IP with network configuration.
