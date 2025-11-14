const { app, BrowserWindow, ipcMain } = require('electron');
const net = require('net');
const path = require('path');

const SOCKET_PATH = '/tmp/python_server.sock';

let mainWindow;
let socketClient = null;
let pendingRequests = new Map(); // Track pending requests: {resolve, reject, timeout}
let messageIdCounter = 0;

// Function to create socket connection (reused for all messages)
function createSocketConnection() {
  return new Promise((resolve, reject) => {
    // If connection already exists and is writable, reuse it
    if (socketClient && socketClient.writable) {
      console.log('Reusing existing connection');
      resolve(socketClient);
      return;
    }
    
    const client = net.createConnection(SOCKET_PATH, () => {
      console.log('Connected to Python server!');
      socketClient = client;
      resolve(client);
    });
    
    // Handle incoming data
    client.on('data', (data) => {
      const response = data.toString().trim();
      console.log('Received from Python:', response);
      
      // Resolve the first pending promise (simple FIFO)
      // In a more complex system, you'd match by request ID
      if (pendingRequests.size > 0) {
        const firstId = pendingRequests.keys().next().value;
        const request = pendingRequests.get(firstId);
        pendingRequests.delete(firstId);
        
        // Clear timeout
        if (request.timeout) {
          clearTimeout(request.timeout);
        }
        
        // Resolve the promise
        request.resolve(response);
      }
    });
    
    client.on('error', (err) => {
      console.log('Socket connection error:', err.message);
      socketClient = null;
      // Reject all pending requests
      pendingRequests.forEach((request) => {
        if (request.timeout) {
          clearTimeout(request.timeout);
        }
        request.reject(err);
      });
      pendingRequests.clear();
      reject(err);
    });
    
    client.on('close', () => {
      console.log('Connection closed');
      socketClient = null;
      // Reject all pending requests
      const closeError = new Error('Connection closed');
      pendingRequests.forEach((request) => {
        if (request.timeout) {
          clearTimeout(request.timeout);
        }
        request.reject(closeError);
      });
      pendingRequests.clear();
    });
  });
}

// Function to send data to Python server
function sendToPython(data) {
  return new Promise((resolve, reject) => {
    const messageId = ++messageIdCounter;
    
    createSocketConnection()
      .then((client) => {
        // Set a timeout to reject if no response
        const timeout = setTimeout(() => {
          if (pendingRequests.has(messageId)) {
            pendingRequests.delete(messageId);
            reject(new Error('Request timeout'));
          }
        }, 10000); // 10 second timeout
        
        // Store the request info
        pendingRequests.set(messageId, { resolve, reject, timeout });
        
        // Send JSON data with newline terminator
        const jsonData = JSON.stringify(data) + '\n';
        client.write(jsonData);
        console.log('Sent to Python:', jsonData.trim());
      })
      .catch((err) => {
        reject(err);
      });
  });
}

// Handle IPC message from renderer
ipcMain.handle('send-data', async (event, data) => {
  try {
    const response = await sendToPython(data);
    return response;
  } catch (error) {
    throw new Error('Failed to send data to Python server: ' + error.message);
  }
});

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');
  
  // Open DevTools (optional, remove in production)
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (socketClient) {
    socketClient.end();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (socketClient) {
    socketClient.end();
  }
});
