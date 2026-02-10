# Mission Control Rebuild Plan

After encountering persistent issues with the current Mission Control implementation, here's a plan to rebuild it from scratch with a simplified architecture:

## 1. Stop all existing servers
```bash
# Kill all existing servers
pkill -f "next dev"
pkill -f "convex dev"
```

## 2. Create a minimal rebuild implementation

### Step 1: Create a simple index.js page
Replace the problematic implementation with a basic page:

```javascript
// File: /Users/karst/.openclaw/workforce/mission-control/src/pages/index.js
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
```

### Step 2: Update _app.js to include Tailwind CSS
```javascript
// File: /Users/karst/.openclaw/workforce/mission-control/src/pages/_app.js
import '@/styles/globals.css'

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
```

### Step 3: Create a minimal globals.css file
```css
/* File: /Users/karst/.openclaw/workforce/mission-control/src/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## 3. Create a startup script
```bash
#!/bin/bash

# Kill any running servers
pkill -f "next dev" || true

# Start Next.js server
cd /Users/karst/.openclaw/workforce/mission-control
npm run dev &
echo "Mission Control is now running at http://localhost:3000"
open http://localhost:3000
```

## 4. Implementation Plan

1. Stop all existing processes
2. Create the simplified files shown above
3. Test the basic app without Convex integration
4. Once that's working, gradually add back database functionality

This approach eliminates the Convex database integration initially to verify that the basic UI works correctly.

## 5. Next Steps

1. Once the basic UI is working, we can re-add database functionality
2. Consider using localStorage for persistence in the short term
3. Re-evaluate whether Convex is the right solution or if we should switch to a simpler database option