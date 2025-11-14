const { app } = require('electron');
const net = require('net');
const path = require('path');

const SOCKET_PATH = '/tmp/python_server.sock';

app.whenReady().then(() => {
  console.log('Connecting to Python server via local socket...');
  
  const client = net.createConnection(SOCKET_PATH, () => {
    console.log('Connected to Python server!\n');
    client.write('hello\n');
    console.log('Sent: hello\n');
  });
  
  client.on('data', (data) => {
    const message = data.toString().trim();
    console.log('Received:', message);
    
    // Respond to server
    if (message === 'hello') {
      client.write('hi\n');
      console.log('Sent: hi\n');
    } else if (message === 'hi') {
      client.write('hello\n');
      console.log('Sent: hello\n');
    }
  });
  
  client.on('close', () => {
    console.log('Connection closed');
  });
  
  client.on('error', (err) => {
    console.log('Error:', err.message);
  });
});

// Prevent app from quitting
app.dock?.hide(); // Hide from dock on macOS
process.on('SIGINT', () => {
  app.quit();
});
