#!/bin/bash

echo "Cleaning up Mission Control project..."

# Kill any running servers
pkill -f "next dev" || true
pkill -f "convex dev" || true
sleep 2

MC_DIR="/Users/karst/.openclaw/workforce/mission-control"

# Remove duplicate files
rm -f "$MC_DIR/pages/_app.tsx" "$MC_DIR/pages/_app.js" "$MC_DIR/pages/index.tsx" "$MC_DIR/pages/index.js" 2>/dev/null
rm -f "$MC_DIR/src/pages/_app.tsx" "$MC_DIR/src/pages/index.tsx" 2>/dev/null

# Backup and remove the .babelrc file causing issues
if [ -f "$MC_DIR/.babelrc" ]; then
  mv "$MC_DIR/.babelrc" "$MC_DIR/.babelrc.bak"
  echo "Backed up .babelrc to .babelrc.bak"
fi

# Create a fresh postcss.config.js
cat > "$MC_DIR/postcss.config.js" << 'EOL'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOL

# Create a fresh tailwind.config.js
cat > "$MC_DIR/tailwind.config.js" << 'EOL'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOL

# Create a fresh next.config.js
cat > "$MC_DIR/next.config.js" << 'EOL'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
EOL

# Add a persistent store
cat > "$MC_DIR/src/utils/store.js" << 'EOL'
// Simple localStorage-based store for tasks
export const saveTask = (task) => {
  try {
    const tasks = getTasks();
    tasks.push(task);
    localStorage.setItem('mission-control-tasks', JSON.stringify(tasks));
    return true;
  } catch (error) {
    console.error('Failed to save task:', error);
    return false;
  }
};

export const getTasks = () => {
  try {
    const tasks = localStorage.getItem('mission-control-tasks');
    return tasks ? JSON.parse(tasks) : [];
  } catch (error) {
    console.error('Failed to get tasks:', error);
    return [];
  }
};

export const updateTask = (taskId, updates) => {
  try {
    const tasks = getTasks();
    const taskIndex = tasks.findIndex(t => t.id === taskId);
    if (taskIndex !== -1) {
      tasks[taskIndex] = { ...tasks[taskIndex], ...updates };
      localStorage.setItem('mission-control-tasks', JSON.stringify(tasks));
      return true;
    }
    return false;
  } catch (error) {
    console.error('Failed to update task:', error);
    return false;
  }
};
EOL

# Update the index.js page to use localStorage
cat > "$MC_DIR/src/pages/index.js" << 'EOL'
import React, { useState, useEffect } from 'react';
import { getTasks, saveTask, updateTask } from '../utils/store';

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [priority, setPriority] = useState('medium');

  // Load tasks on component mount
  useEffect(() => {
    const storedTasks = getTasks();
    setTasks(storedTasks);
  }, []);

  const addTask = () => {
    if (!newTask.trim()) return;
    
    const task = {
      id: Date.now().toString(),
      title: newTask,
      description: taskDescription,
      status: 'inbox',
      priority,
      createdAt: new Date().toISOString()
    };
    
    // Save to localStorage
    saveTask(task);
    
    // Update UI
    setTasks([...tasks, task]);
    setNewTask('');
    setTaskDescription('');
    setIsModalOpen(false);
  };

  const changeTaskStatus = (taskId, newStatus) => {
    // Update in localStorage
    updateTask(taskId, { status: newStatus });
    
    // Update UI
    setTasks(tasks.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    ));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
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
              <div 
                key={task.id} 
                className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-blue-500"
                onClick={() => changeTaskStatus(task.id, 'assigned')}
              >
                <h3 className="font-medium">{task.title}</h3>
                {task.description && <p className="text-sm text-gray-600 mt-1">{task.description}</p>}
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span className="capitalize">{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">Assigned</h2>
            {tasks.filter(t => t.status === 'assigned').map(task => (
              <div 
                key={task.id} 
                className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-yellow-500"
                onClick={() => changeTaskStatus(task.id, 'in-progress')}
              >
                <h3 className="font-medium">{task.title}</h3>
                {task.description && <p className="text-sm text-gray-600 mt-1">{task.description}</p>}
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span className="capitalize">{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">In Progress</h2>
            {tasks.filter(t => t.status === 'in-progress').map(task => (
              <div 
                key={task.id} 
                className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-purple-500"
                onClick={() => changeTaskStatus(task.id, 'completed')}
              >
                <h3 className="font-medium">{task.title}</h3>
                {task.description && <p className="text-sm text-gray-600 mt-1">{task.description}</p>}
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span className="capitalize">{task.priority}</span>
                  <span>{new Date(task.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-md shadow-md p-4">
            <h2 className="font-semibold mb-4">Completed</h2>
            {tasks.filter(t => t.status === 'completed').map(task => (
              <div 
                key={task.id} 
                className="bg-gray-50 p-3 rounded-md mb-2 border-l-4 border-green-500"
              >
                <h3 className="font-medium">{task.title}</h3>
                {task.description && <p className="text-sm text-gray-600 mt-1">{task.description}</p>}
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span className="capitalize">{task.priority}</span>
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
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2 h-24"
                  placeholder="Enter task description"
                ></textarea>
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
                  disabled={!newTask.trim()}
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

# Kill any running servers and start the Next.js server
echo "Starting Mission Control..."
cd "$MC_DIR"
npm run dev &
SERVER_PID=$!

# Wait a bit for the server to start
sleep 5
echo "Mission Control is now running at http://localhost:3000"
echo "This version uses localStorage for persistence - no database required."
open http://localhost:3000

echo "Cleaned and simplified Mission Control has been rebuilt and should be working now."