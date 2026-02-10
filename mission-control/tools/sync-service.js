// sync-service.js - Local synchronization service for Mission Control
//
// This script provides a simple local synchronization service
// for the Mission Control dashboard when running locally

const fs = require('fs');
const path = require('path');
const http = require('http');

const KANBAN_DATA_PATH = path.resolve(__dirname, '../src/app/api/kanban-data/route.ts');
const CHECK_INTERVAL_MS = 2000; // Check for changes every 2 seconds

let lastModifiedTime = 0;
let isFirstRun = true;

function getCurrentKanbanData() {
  try {
    const fileContent = fs.readFileSync(KANBAN_DATA_PATH, 'utf8');
    
    // Extract the KANBAN_DATA object from the file
    const match = fileContent.match(/const KANBAN_DATA = ({[\s\S]*?});/);
    if (!match || !match[1]) {
      console.error('Could not extract KANBAN_DATA from file');
      return null;
    }
    
    // Parse the data object
    // Note: This is a safe eval since we're reading our own code file
    const dataObj = eval(`(${match[1]})`);
    return dataObj;
  } catch (error) {
    console.error('Error reading kanban data:', error);
    return null;
  }
}

function checkForChanges() {
  try {
    const stats = fs.statSync(KANBAN_DATA_PATH);
    const mtime = stats.mtimeMs;
    
    if (isFirstRun) {
      console.log('Initial sync service setup complete');
      lastModifiedTime = mtime;
      isFirstRun = false;
      return;
    }
    
    // Check if file has been modified since last check
    if (mtime > lastModifiedTime) {
      console.log(`Changes detected at ${new Date().toLocaleTimeString()}`);
      lastModifiedTime = mtime;
      
      // Get current data
      const data = getCurrentKanbanData();
      if (!data) return;
      
      // In a real implementation, this would broadcast to connected clients
      console.log(`Updated data: Last updated ${data.lastUpdated}, ${data.columns.reduce((sum, col) => sum + col.tasks.length, 0)} tasks`);
    }
  } catch (error) {
    console.error('Error checking for changes:', error);
  }
}

// Start the check interval
console.log('Starting sync service...');
checkForChanges(); // Initial check
setInterval(checkForChanges, CHECK_INTERVAL_MS);

// Create a simple HTTP server to validate the sync service is running
const server = http.createServer((req, res) => {
  if (req.url === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'running', 
      lastCheck: new Date().toISOString(),
      dataFile: KANBAN_DATA_PATH
    }));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Mission Control Sync Service');
  }
});

const PORT = 3030;
server.listen(PORT, () => {
  console.log(`Sync service listening at http://localhost:${PORT}`);
  console.log(`Check status at http://localhost:${PORT}/status`);
});