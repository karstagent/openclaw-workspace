#!/bin/bash

echo "Rebuilding Mission Control with a simplified approach..."

# Kill all existing servers
pkill -f "next dev" || true
pkill -f "convex dev" || true
sleep 2

# Ensure required directories exist
MC_DIR="/Users/karst/.openclaw/workforce/mission-control"
mkdir -p "$MC_DIR/src/pages"
mkdir -p "$MC_DIR/src/styles"

# Create the simplified index.js page
cat > "$MC_DIR/src/pages/index.js" << 'EOL'
import React, { useState, useEffect } from 'react';

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [priority, setPriority] = useState('medium');

  const addTask = () => {
    if (!newTask.trim()) return;
    
    const task = {
      id: Date.now().toString(),
      title: newTask,
      status: 'inbox',
      priority,
      createdAt: new Date().toISOString()
    };
    
    setTasks([...tasks, task]);
    setNewTask('');
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Mission Control</h1>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            New Task
          </button>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Task Columns */}
          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">Inbox</h2>
            {tasks.filter(t => t.status === 'inbox').map(task => (
              <div key={task.id} className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-blue-500">
                <h3 className="font-medium">{task.title}</h3>
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">Assigned</h2>
            {tasks.filter(t => t.status === 'assigned').map(task => (
              <div key={task.id} className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-yellow-500">
                <h3 className="font-medium">{task.title}</h3>
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">In Progress</h2>
            {tasks.filter(t => t.status === 'in-progress').map(task => (
              <div key={task.id} className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-purple-500">
                <h3 className="font-medium">{task.title}</h3>
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">Completed</h2>
            {tasks.filter(t => t.status === 'completed').map(task => (
              <div key={task.id} className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-green-500">
                <h3 className="font-medium">{task.title}</h3>
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Task Name</label>
                <input
                  type="text"
                  value={newTask}
                  onChange={(e) => setNewTask(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                  placeholder="Enter task name"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md"
                >
                  Cancel
                </button>
                <button
                  onClick={addTask}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md"
                >
                  Create Task
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
EOL

# Create the _app.js file
cat > "$MC_DIR/src/pages/_app.js" << 'EOL'
import '@/styles/globals.css'

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
EOL

# Create the globals.css file
cat > "$MC_DIR/src/styles/globals.css" << 'EOL'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOL

# Kill any running servers and start the Next.js server
echo "Starting Mission Control..."
cd "$MC_DIR"
npm run dev &
SERVER_PID=$!

# Wait a bit for the server to start
sleep 5
echo "Mission Control is now running at http://localhost:3000"
open http://localhost:3000

echo "Simplified Mission Control has been rebuilt and should be working now."
echo "If you still encounter issues, you may need to restart the server manually."
echo "To do so, run: cd $MC_DIR && npm run dev"