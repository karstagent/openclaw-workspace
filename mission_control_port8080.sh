#!/bin/bash

# Kill any existing Python servers
echo "Stopping any existing servers..."
pkill -f "python3 server.py" || true
sleep 2

# Create a Mission Control on port 8080
echo "Creating Mission Control on port 8080..."

# Navigate to the workforce directory
cd /Users/karst/.openclaw/workforce || exit

# Create or use simple-mission-control directory
mkdir -p simple-mission-control
cat > simple-mission-control/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission Control - Port 8080</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .task-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .task-card:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto p-4 max-w-6xl">
        <header class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">Mission Control (Port 8080)</h1>
            <button 
                id="newTaskBtn"
                class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
                New Task
            </button>
        </header>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Inbox Column -->
            <div class="bg-white rounded-md shadow-md p-4">
                <h2 class="font-semibold mb-4">Inbox</h2>
                <div id="inbox-tasks" class="space-y-2"></div>
            </div>
            
            <!-- Assigned Column -->
            <div class="bg-white rounded-md shadow-md p-4">
                <h2 class="font-semibold mb-4">Assigned</h2>
                <div id="assigned-tasks" class="space-y-2"></div>
            </div>
            
            <!-- In Progress Column -->
            <div class="bg-white rounded-md shadow-md p-4">
                <h2 class="font-semibold mb-4">In Progress</h2>
                <div id="in-progress-tasks" class="space-y-2"></div>
            </div>
            
            <!-- Completed Column -->
            <div class="bg-white rounded-md shadow-md p-4">
                <h2 class="font-semibold mb-4">Completed</h2>
                <div id="completed-tasks" class="space-y-2"></div>
            </div>
        </div>
        
        <!-- Task Creation Modal -->
        <div id="taskModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
            <div class="bg-white rounded-lg p-6 max-w-md w-full">
                <h2 class="text-xl font-semibold mb-4">Create New Task</h2>
                
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Task Name</label>
                    <input
                        id="taskName"
                        type="text"
                        class="w-full border border-gray-300 rounded-md p-2"
                        placeholder="Enter task name"
                    />
                </div>
                
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Description</label>
                    <textarea
                        id="taskDescription"
                        class="w-full border border-gray-300 rounded-md p-2 h-24"
                        placeholder="Enter task description"
                    ></textarea>
                </div>
                
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Priority</label>
                    <select
                        id="taskPriority"
                        class="w-full border border-gray-300 rounded-md p-2"
                    >
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                    </select>
                </div>
                
                <div class="flex justify-end space-x-2">
                    <button
                        id="cancelTaskBtn"
                        class="px-4 py-2 border border-gray-300 rounded-md"
                    >
                        Cancel
                    </button>
                    <button
                        id="createTaskBtn"
                        class="px-4 py-2 bg-blue-600 text-white rounded-md"
                    >
                        Create Task
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Task data structure
        const getTasks = () => {
            try {
                return JSON.parse(localStorage.getItem('mission-control-tasks')) || [];
            } catch (e) {
                console.error('Error loading tasks', e);
                return [];
            }
        };
        
        const saveTasks = (tasks) => {
            localStorage.setItem('mission-control-tasks', JSON.stringify(tasks));
        };
        
        // Render all tasks
        const renderTasks = () => {
            const tasks = getTasks();
            
            // Clear all task containers
            document.getElementById('inbox-tasks').innerHTML = '';
            document.getElementById('assigned-tasks').innerHTML = '';
            document.getElementById('in-progress-tasks').innerHTML = '';
            document.getElementById('completed-tasks').innerHTML = '';
            
            // Sort tasks by creation date (newest first)
            tasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            
            // Render tasks in their respective columns
            tasks.forEach(task => {
                let container;
                let borderColor;
                
                switch(task.status) {
                    case 'inbox':
                        container = document.getElementById('inbox-tasks');
                        borderColor = 'border-blue-500';
                        break;
                    case 'assigned':
                        container = document.getElementById('assigned-tasks');
                        borderColor = 'border-yellow-500';
                        break;
                    case 'in-progress':
                        container = document.getElementById('in-progress-tasks');
                        borderColor = 'border-purple-500';
                        break;
                    case 'completed':
                        container = document.getElementById('completed-tasks');
                        borderColor = 'border-green-500';
                        break;
                    default:
                        container = document.getElementById('inbox-tasks');
                        borderColor = 'border-blue-500';
                }
                
                const taskEl = document.createElement('div');
                taskEl.className = `task-card bg-gray-50 p-3 rounded-md border-l-4 ${borderColor}`;
                taskEl.dataset.id = task.id;
                
                taskEl.innerHTML = `
                    <h3 class="font-medium">${task.title}</h3>
                    ${task.description ? `<p class="text-sm text-gray-600 mt-1">${task.description}</p>` : ''}
                    <div class="flex justify-between text-sm text-gray-500 mt-2">
                        <span class="capitalize">${task.priority}</span>
                        <span>${new Date(task.createdAt).toLocaleDateString()}</span>
                    </div>
                `;
                
                // Add click handler to move the task to the next status
                // (except for completed tasks)
                if (task.status !== 'completed') {
                    taskEl.addEventListener('click', () => {
                        let newStatus;
                        
                        switch(task.status) {
                            case 'inbox':
                                newStatus = 'assigned';
                                break;
                            case 'assigned':
                                newStatus = 'in-progress';
                                break;
                            case 'in-progress':
                                newStatus = 'completed';
                                break;
                            default:
                                newStatus = task.status;
                        }
                        
                        // Update task status
                        const tasks = getTasks();
                        const updatedTasks = tasks.map(t => 
                            t.id === task.id ? { ...t, status: newStatus } : t
                        );
                        
                        saveTasks(updatedTasks);
                        renderTasks();
                    });
                }
                
                container.appendChild(taskEl);
            });
        };
        
        // Modal functionality
        const taskModal = document.getElementById('taskModal');
        const newTaskBtn = document.getElementById('newTaskBtn');
        const cancelTaskBtn = document.getElementById('cancelTaskBtn');
        const createTaskBtn = document.getElementById('createTaskBtn');
        
        newTaskBtn.addEventListener('click', () => {
            taskModal.classList.remove('hidden');
            document.getElementById('taskName').focus();
        });
        
        cancelTaskBtn.addEventListener('click', () => {
            taskModal.classList.add('hidden');
            resetTaskForm();
        });
        
        createTaskBtn.addEventListener('click', () => {
            const taskName = document.getElementById('taskName').value.trim();
            if (!taskName) {
                alert('Please enter a task name');
                return;
            }
            
            const task = {
                id: Date.now().toString(),
                title: taskName,
                description: document.getElementById('taskDescription').value.trim(),
                priority: document.getElementById('taskPriority').value,
                status: 'inbox',
                createdAt: new Date().toISOString()
            };
            
            const tasks = getTasks();
            tasks.push(task);
            saveTasks(tasks);
            
            taskModal.classList.add('hidden');
            resetTaskForm();
            renderTasks();
        });
        
        const resetTaskForm = () => {
            document.getElementById('taskName').value = '';
            document.getElementById('taskDescription').value = '';
            document.getElementById('taskPriority').value = 'medium';
        };
        
        // Initialize the app
        document.addEventListener('DOMContentLoaded', () => {
            renderTasks();
            
            // Create sample tasks if none exist
            const tasks = getTasks();
            if (tasks.length === 0) {
                const sampleTasks = [
                    {
                        id: '1',
                        title: 'Welcome to Mission Control',
                        description: 'Click on this task to move it to the Assigned column.',
                        priority: 'medium',
                        status: 'inbox',
                        createdAt: new Date().toISOString()
                    }
                ];
                saveTasks(sampleTasks);
                renderTasks();
            }
        });
        
        // Ensure tasks render even if DOMContentLoaded already fired
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderTasks);
        } else {
            renderTasks();
        }
    </script>
</body>
</html>
EOL

# Create a Python server script for port 8080
cat > simple-mission-control/server8080.py << 'EOL'
#!/usr/bin/env python3
import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

PORT = 8080

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for all paths
        if self.path == '/' or not os.path.exists(os.path.join(os.getcwd(), self.path[1:])):
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Change to the directory containing the HTML file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Start the server
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Mission Control is running at http://localhost:{PORT}")
    # Open the browser
    webbrowser.open(f'http://localhost:{PORT}')
    # Serve until interrupted
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
EOL

# Make the server script executable
chmod +x simple-mission-control/server8080.py

# Create a standalone HTML file that can be opened directly
cat > /Users/karst/.openclaw/workspace/mission_control.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission Control - Standalone File</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .task-card {
            transition: transform 0.2s;
            cursor: pointer;
            margin-bottom: 0.5rem;
        }
        .task-card:hover {
            transform: translateY(-2px);
        }
        body {
            background-color: #f3f4f6;
            min-height: 100vh;
            padding: 1rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        h1 {
            font-size: 1.5rem;
            font-weight: bold;
        }
        button.new-task {
            background-color: #2563eb;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
        }
        button.new-task:hover {
            background-color: #1d4ed8;
        }
        .board {
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: 1rem;
        }
        @media (min-width: 768px) {
            .board {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        .column {
            background-color: white;
            border-radius: 0.375rem;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            padding: 1rem;
        }
        .column h2 {
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .tasks {
            display: flex;
            flex-direction: column;
        }
        .task-card {
            background-color: #f9fafb;
            padding: 0.75rem;
            border-radius: 0.375rem;
        }
        .task-blue {
            border-left: 4px solid #3b82f6;
        }
        .task-yellow {
            border-left: 4px solid #eab308;
        }
        .task-purple {
            border-left: 4px solid #a855f7;
        }
        .task-green {
            border-left: 4px solid #22c55e;
        }
        .task-title {
            font-weight: 500;
        }
        .task-description {
            font-size: 0.875rem;
            color: #4b5563;
            margin-top: 0.25rem;
        }
        .task-footer {
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
            color: #6b7280;
            margin-top: 0.5rem;
        }
        .task-priority {
            text-transform: capitalize;
        }
        .modal {
            position: fixed;
            inset: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50;
        }
        .modal.hidden {
            display: none;
        }
        .modal-content {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            max-width: 28rem;
            width: 100%;
        }
        .modal-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        .form-input {
            width: 100%;
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }
        .form-textarea {
            width: 100%;
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
            height: 6rem;
        }
        .form-select {
            width: 100%;
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            padding: 0.5rem;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
        }
        .btn-cancel {
            padding: 0.5rem 1rem;
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
        }
        .btn-create {
            padding: 0.5rem 1rem;
            background-color: #2563eb;
            color: white;
            border-radius: 0.375rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Mission Control (Standalone File)</h1>
            <button id="newTaskBtn" class="new-task">New Task</button>
        </header>
        
        <div class="board">
            <!-- Inbox Column -->
            <div class="column">
                <h2>Inbox</h2>
                <div id="inbox-tasks" class="tasks"></div>
            </div>
            
            <!-- Assigned Column -->
            <div class="column">
                <h2>Assigned</h2>
                <div id="assigned-tasks" class="tasks"></div>
            </div>
            
            <!-- In Progress Column -->
            <div class="column">
                <h2>In Progress</h2>
                <div id="in-progress-tasks" class="tasks"></div>
            </div>
            
            <!-- Completed Column -->
            <div class="column">
                <h2>Completed</h2>
                <div id="completed-tasks" class="tasks"></div>
            </div>
        </div>
        
        <!-- Task Creation Modal -->
        <div id="taskModal" class="modal hidden">
            <div class="modal-content">
                <h2 class="modal-title">Create New Task</h2>
                
                <div class="form-group">
                    <label class="form-label" for="taskName">Task Name</label>
                    <input
                        id="taskName"
                        type="text"
                        class="form-input"
                        placeholder="Enter task name"
                    />
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="taskDescription">Description</label>
                    <textarea
                        id="taskDescription"
                        class="form-textarea"
                        placeholder="Enter task description"
                    ></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="taskPriority">Priority</label>
                    <select
                        id="taskPriority"
                        class="form-select"
                    >
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                    </select>
                </div>
                
                <div class="modal-actions">
                    <button
                        id="cancelTaskBtn"
                        class="btn-cancel"
                    >
                        Cancel
                    </button>
                    <button
                        id="createTaskBtn"
                        class="btn-create"
                    >
                        Create Task
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Task data structure
        const getTasks = () => {
            try {
                return JSON.parse(localStorage.getItem('mission-control-tasks')) || [];
            } catch (e) {
                console.error('Error loading tasks', e);
                return [];
            }
        };
        
        const saveTasks = (tasks) => {
            localStorage.setItem('mission-control-tasks', JSON.stringify(tasks));
        };
        
        // Render all tasks
        const renderTasks = () => {
            const tasks = getTasks();
            
            // Clear all task containers
            document.getElementById('inbox-tasks').innerHTML = '';
            document.getElementById('assigned-tasks').innerHTML = '';
            document.getElementById('in-progress-tasks').innerHTML = '';
            document.getElementById('completed-tasks').innerHTML = '';
            
            // Sort tasks by creation date (newest first)
            tasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            
            // Render tasks in their respective columns
            tasks.forEach(task => {
                let container;
                let borderClass;
                
                switch(task.status) {
                    case 'inbox':
                        container = document.getElementById('inbox-tasks');
                        borderClass = 'task-blue';
                        break;
                    case 'assigned':
                        container = document.getElementById('assigned-tasks');
                        borderClass = 'task-yellow';
                        break;
                    case 'in-progress':
                        container = document.getElementById('in-progress-tasks');
                        borderClass = 'task-purple';
                        break;
                    case 'completed':
                        container = document.getElementById('completed-tasks');
                        borderClass = 'task-green';
                        break;
                    default:
                        container = document.getElementById('inbox-tasks');
                        borderClass = 'task-blue';
                }
                
                const taskEl = document.createElement('div');
                taskEl.className = `task-card ${borderClass}`;
                taskEl.dataset.id = task.id;
                
                taskEl.innerHTML = `
                    <h3 class="task-title">${task.title}</h3>
                    ${task.description ? `<p class="task-description">${task.description}</p>` : ''}
                    <div class="task-footer">
                        <span class="task-priority">${task.priority}</span>
                        <span>${new Date(task.createdAt).toLocaleDateString()}</span>
                    </div>
                `;
                
                // Add click handler to move the task to the next status
                // (except for completed tasks)
                if (task.status !== 'completed') {
                    taskEl.addEventListener('click', () => {
                        let newStatus;
                        
                        switch(task.status) {
                            case 'inbox':
                                newStatus = 'assigned';
                                break;
                            case 'assigned':
                                newStatus = 'in-progress';
                                break;
                            case 'in-progress':
                                newStatus = 'completed';
                                break;
                            default:
                                newStatus = task.status;
                        }
                        
                        // Update task status
                        const tasks = getTasks();
                        const updatedTasks = tasks.map(t => 
                            t.id === task.id ? { ...t, status: newStatus } : t
                        );
                        
                        saveTasks(updatedTasks);
                        renderTasks();
                    });
                }
                
                container.appendChild(taskEl);
            });
        };
        
        // Modal functionality
        const taskModal = document.getElementById('taskModal');
        const newTaskBtn = document.getElementById('newTaskBtn');
        const cancelTaskBtn = document.getElementById('cancelTaskBtn');
        const createTaskBtn = document.getElementById('createTaskBtn');
        
        newTaskBtn.addEventListener('click', () => {
            taskModal.classList.remove('hidden');
            document.getElementById('taskName').focus();
        });
        
        cancelTaskBtn.addEventListener('click', () => {
            taskModal.classList.add('hidden');
            resetTaskForm();
        });
        
        createTaskBtn.addEventListener('click', () => {
            const taskName = document.getElementById('taskName').value.trim();
            if (!taskName) {
                alert('Please enter a task name');
                return;
            }
            
            const task = {
                id: Date.now().toString(),
                title: taskName,
                description: document.getElementById('taskDescription').value.trim(),
                priority: document.getElementById('taskPriority').value,
                status: 'inbox',
                createdAt: new Date().toISOString()
            };
            
            const tasks = getTasks();
            tasks.push(task);
            saveTasks(tasks);
            
            taskModal.classList.add('hidden');
            resetTaskForm();
            renderTasks();
        });
        
        const resetTaskForm = () => {
            document.getElementById('taskName').value = '';
            document.getElementById('taskDescription').value = '';
            document.getElementById('taskPriority').value = 'medium';
        };
        
        // Initialize the app
        document.addEventListener('DOMContentLoaded', () => {
            renderTasks();
            
            // Create sample tasks if none exist
            const tasks = getTasks();
            if (tasks.length === 0) {
                const sampleTasks = [
                    {
                        id: '1',
                        title: 'Welcome to Mission Control',
                        description: 'Click on this task to move it to the Assigned column.',
                        priority: 'medium',
                        status: 'inbox',
                        createdAt: new Date().toISOString()
                    }
                ];
                saveTasks(sampleTasks);
                renderTasks();
            }
        });
        
        // Ensure tasks render even if DOMContentLoaded already fired
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderTasks);
        } else {
            renderTasks();
        }
    </script>
</body>
</html>
EOL

# Start the server on port 8080
cd /Users/karst/.openclaw/workforce/simple-mission-control
python3 server8080.py &

echo "Mission Control has been set up in multiple ways:"
echo "1. Running on port 8080: http://localhost:8080"
echo "2. Standalone HTML file: /Users/karst/.openclaw/workspace/mission_control.html"
echo ""
echo "If you still can't access the web server version, try opening the standalone HTML file directly:"
echo "open /Users/karst/.openclaw/workspace/mission_control.html"