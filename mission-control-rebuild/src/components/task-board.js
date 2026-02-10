/**
 * Task Board Component
 * Kanban-style board for visualizing and managing tasks
 */

class TaskBoard extends Component {
    init() {
        super.init();
        
        // Initialize properties
        this.tasks = [];
        this.projects = [];
        this.users = [];
        this.draggedTask = null;
        this.filters = this.options.filters || {
            status: null,
            priority: null,
            assignee: null,
            project: null,
            search: '',
            dueDate: null
        };
        
        // Define columns
        this.columns = [
            { id: 'inbox', label: 'Inbox', icon: 'inbox' },
            { id: 'assigned', label: 'Assigned', icon: 'user' },
            { id: 'in-progress', label: 'In Progress', icon: 'clock' },
            { id: 'completed', label: 'Completed', icon: 'check' }
        ];
        
        // Subscribe to state changes
        this.subscribe('tasks.items', (tasks) => {
            this.tasks = tasks;
            this.renderTasks();
        });
        
        this.subscribe('projects.items', (projects) => {
            this.projects = projects;
            this.renderTasks(); // Re-render to update project information
        });
        
        this.subscribe('users.items', (users) => {
            this.users = users;
            this.renderTasks(); // Re-render to update assignee information
        });
        
        this.subscribe('tasks.filters', (filters) => {
            this.filters = filters;
            this.renderTasks();
        });
        
        // Listen for task events
        EventBus.subscribe(Events.TASK_CREATED, (task) => {
            this.loadTasks();
        });
        
        EventBus.subscribe(Events.TASK_UPDATED, (task) => {
            this.loadTasks();
        });
        
        EventBus.subscribe(Events.TASK_DELETED, (taskId) => {
            this.loadTasks();
        });
    }
    
    render() {
        // Create board layout
        let html = `
            <div class="task-board">
                <!-- Board Header with Filters -->
                <div class="mb-4 glass dark:glass-dark rounded-lg p-4">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                        <h2 class="text-xl font-semibold">Task Board</h2>
                        <div class="flex space-x-2 mt-2 sm:mt-0">
                            <button id="new-task-button" class="btn-primary inline-flex items-center px-3 py-1.5 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                <svg class="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                                New Task
                            </button>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <!-- Project Filter -->
                        <div>
                            <label for="filter-project" class="block text-sm font-medium mb-1">Project</label>
                            <select id="filter-project" class="glass dark:glass-dark w-full rounded-md py-1.5 px-3 text-sm">
                                <option value="">All Projects</option>
                                <!-- Projects will be loaded here -->
                            </select>
                        </div>
                        
                        <!-- Assignee Filter -->
                        <div>
                            <label for="filter-assignee" class="block text-sm font-medium mb-1">Assignee</label>
                            <select id="filter-assignee" class="glass dark:glass-dark w-full rounded-md py-1.5 px-3 text-sm">
                                <option value="">All Assignees</option>
                                <!-- Users will be loaded here -->
                            </select>
                        </div>
                        
                        <!-- Priority Filter -->
                        <div>
                            <label for="filter-priority" class="block text-sm font-medium mb-1">Priority</label>
                            <select id="filter-priority" class="glass dark:glass-dark w-full rounded-md py-1.5 px-3 text-sm">
                                <option value="">All Priorities</option>
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                        
                        <!-- Due Date Filter -->
                        <div>
                            <label for="filter-due-date" class="block text-sm font-medium mb-1">Due Date</label>
                            <select id="filter-due-date" class="glass dark:glass-dark w-full rounded-md py-1.5 px-3 text-sm">
                                <option value="">Any Time</option>
                                <option value="today">Today</option>
                                <option value="tomorrow">Tomorrow</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                                <option value="overdue">Overdue</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Task Columns -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    ${this.columns.map(column => `
                        <div class="glass dark:glass-dark rounded-lg shadow overflow-hidden flex flex-col">
                            <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                                <h3 class="font-semibold flex items-center">
                                    ${this.getColumnIcon(column.icon)}
                                    <span class="ml-2">${column.label}</span>
                                </h3>
                                <span id="${column.id}-count" class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700 text-xs font-medium">0</span>
                            </div>
                            <div id="${column.id}-tasks" class="task-column p-2 flex-1 overflow-y-auto max-h-[70vh] min-h-[300px]" data-column="${column.id}">
                                <div class="tasks-loading text-center py-4">
                                    <div class="w-6 h-6 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto mb-2"></div>
                                    <p class="text-sm text-gray-500 dark:text-gray-400">Loading tasks...</p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Empty State -->
                <div id="empty-state" class="hidden mt-8 text-center py-12 glass dark:glass-dark rounded-lg">
                    <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                    <h3 class="mt-2 text-lg font-medium">No tasks found</h3>
                    <p class="mt-1 text-gray-500 dark:text-gray-400">Get started by creating a new task.</p>
                    <div class="mt-6">
                        <button id="empty-new-task-button" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            New Task
                        </button>
                    </div>
                </div>
                
                <!-- Task Detail Modal -->
                <div id="task-detail-modal" class="hidden fixed z-50 inset-0 overflow-y-auto">
                    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
                        
                        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
                        
                        <div id="task-detail-content" class="glass dark:glass-dark inline-block align-bottom rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div class="p-6">
                                <div class="w-6 h-6 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Edit Task Modal -->
                <div id="edit-task-modal" class="hidden fixed z-50 inset-0 overflow-y-auto">
                    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
                        
                        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
                        
                        <div id="edit-task-content" class="glass dark:glass-dark inline-block align-bottom rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div class="p-6">
                                <div class="w-6 h-6 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.el.innerHTML = html;
        
        // Load data
        this.loadData();
    }
    
    setupEvents() {
        // New task button
        this.on('#new-task-button, #empty-new-task-button', 'click', () => {
            this.openNewTaskModal();
        });
        
        // Set up filters
        this.on('#filter-project', 'change', (e) => {
            this.filters.project = e.target.value || null;
            State.set('tasks.filters', this.filters);
        });
        
        this.on('#filter-assignee', 'change', (e) => {
            this.filters.assignee = e.target.value || null;
            State.set('tasks.filters', this.filters);
        });
        
        this.on('#filter-priority', 'change', (e) => {
            this.filters.priority = e.target.value || null;
            State.set('tasks.filters', this.filters);
        });
        
        this.on('#filter-due-date', 'change', (e) => {
            this.filters.dueDate = e.target.value || null;
            State.set('tasks.filters', this.filters);
        });
        
        // Set up drag and drop for task columns
        this.setupDragAndDrop();
    }
    
    /**
     * Load tasks, projects, and users data
     */
    async loadData() {
        try {
            // Load all data concurrently
            const [tasks, projects, users] = await Promise.all([
                Storage.getAll('tasks'),
                Storage.getAll('projects'),
                Storage.getAll('users')
            ]);
            
            // Update state with loaded data
            State.set('tasks.items', tasks);
            State.set('projects.items', projects);
            State.set('users.items', users);
            
            // Update filter dropdowns
            this.updateFilterDropdowns(projects, users);
        } catch (error) {
            console.error('Failed to load data', error);
            Toast.error('Failed to load task board data. Please try again.');
        }
    }
    
    /**
     * Refresh task data
     */
    async loadTasks() {
        try {
            const tasks = await Storage.getAll('tasks');
            State.set('tasks.items', tasks);
        } catch (error) {
            console.error('Failed to load tasks', error);
        }
    }
    
    /**
     * Update filter dropdowns with projects and users
     */
    updateFilterDropdowns(projects, users) {
        // Project dropdown
        const projectDropdown = this.find('#filter-project');
        
        if (projects.length > 0) {
            let projectOptions = '<option value="">All Projects</option>';
            
            // Sort projects by name
            projects.sort((a, b) => a.name.localeCompare(b.name));
            
            projects.forEach(project => {
                projectOptions += `<option value="${project.id}">${project.name}</option>`;
            });
            
            projectDropdown.innerHTML = projectOptions;
        }
        
        // Assignee dropdown
        const assigneeDropdown = this.find('#filter-assignee');
        
        if (users.length > 0) {
            let assigneeOptions = '<option value="">All Assignees</option>';
            
            // Sort users by name
            users.sort((a, b) => a.name.localeCompare(b.name));
            
            users.forEach(user => {
                assigneeOptions += `<option value="${user.id}">${user.name}</option>`;
            });
            
            assigneeDropdown.innerHTML = assigneeOptions;
        }
        
        // Set initial filter values if they exist
        if (this.filters.project) {
            projectDropdown.value = this.filters.project;
        }
        
        if (this.filters.assignee) {
            assigneeDropdown.value = this.filters.assignee;
        }
        
        if (this.filters.priority) {
            this.find('#filter-priority').value = this.filters.priority;
        }
        
        if (this.filters.dueDate) {
            this.find('#filter-due-date').value = this.filters.dueDate;
        }
    }
    
    /**
     * Render tasks into their respective columns
     */
    renderTasks() {
        // Apply filters to tasks
        const filteredTasks = this.filterTasks();
        
        // Group tasks by status
        const tasksByStatus = this.groupTasksByStatus(filteredTasks);
        
        // Check if there are any tasks to display
        const hasAnyTasks = Object.values(tasksByStatus).some(tasks => tasks.length > 0);
        
        // Show/hide empty state
        const emptyState = this.find('#empty-state');
        emptyState.classList.toggle('hidden', hasAnyTasks);
        
        // Render each column
        this.columns.forEach(column => {
            const columnTasks = tasksByStatus[column.id] || [];
            this.renderColumn(column.id, columnTasks);
        });
    }
    
    /**
     * Render a single column with its tasks
     */
    renderColumn(columnId, tasks) {
        const columnElement = this.find(`#${columnId}-tasks`);
        const countElement = this.find(`#${columnId}-count`);
        
        // Update count
        countElement.textContent = tasks.length.toString();
        
        // Clear previous tasks
        columnElement.innerHTML = '';
        
        // If no tasks, show empty message
        if (tasks.length === 0) {
            columnElement.innerHTML = `
                <div class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                    <p>No tasks</p>
                </div>
            `;
            return;
        }
        
        // Render tasks
        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-card glass dark:glass-dark rounded-lg p-3 mb-3 hover-lift cursor-pointer';
            taskElement.dataset.id = task.id;
            
            // Get project details if available
            let projectBadge = '';
            if (task.projectId) {
                const project = this.projects.find(p => p.id === task.projectId);
                if (project) {
                    projectBadge = `
                        <span class="inline-flex items-center text-xs font-medium mr-2">
                            <span class="w-2 h-2 rounded-full mr-1" style="background-color: ${project.color || '#3b82f6'}"></span>
                            ${project.name}
                        </span>
                    `;
                }
            }
            
            // Get assignee details if available
            let assigneeBadge = '';
            if (task.assigneeId) {
                const assignee = this.users.find(u => u.id === task.assigneeId);
                if (assignee) {
                    assigneeBadge = `
                        <span class="inline-flex items-center text-xs font-medium">
                            <img class="w-4 h-4 rounded-full mr-1" src="${assignee.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(assignee.name) + '&size=32'}" alt="${assignee.name}">
                            ${assignee.name}
                        </span>
                    `;
                }
            }
            
            // Get priority class
            const priorityClass = Helpers.getPriorityClass(task.priority);
            
            // Format due date
            let dueDateText = '';
            let dueDateClass = '';
            
            if (task.dueDate) {
                const isPastDue = Helpers.isPastDue(task.dueDate);
                dueDateText = Helpers.formatDueDate(task.dueDate);
                dueDateClass = isPastDue ? 'text-red-600 dark:text-red-400' : '';
            }
            
            taskElement.innerHTML = `
                <div class="${priorityClass}">
                    <div class="flex justify-between items-start">
                        <h3 class="font-medium">${task.title}</h3>
                        <span class="inline-block text-xs px-2 py-0.5 rounded-full ${this.getPriorityBadgeClass(task.priority)}">${task.priority}</span>
                    </div>
                    
                    ${task.description ? `<p class="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">${task.description}</p>` : ''}
                    
                    <div class="mt-2 flex flex-wrap items-center text-xs text-gray-500 dark:text-gray-400">
                        ${projectBadge}
                        ${assigneeBadge}
                    </div>
                    
                    ${task.dueDate ? `
                        <div class="mt-2 text-xs ${dueDateClass}">
                            <svg class="inline-block w-3 h-3 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            ${dueDateText}
                        </div>
                    ` : ''}
                </div>
            `;
            
            // Open task detail on click
            taskElement.addEventListener('click', () => {
                this.openTaskDetail(task.id);
            });
            
            // Make the task draggable
            taskElement.draggable = true;
            taskElement.addEventListener('dragstart', (e) => {
                this.handleDragStart(e, task.id);
            });
            
            columnElement.appendChild(taskElement);
        });
    }
    
    /**
     * Filter tasks based on current filters
     */
    filterTasks() {
        if (!this.tasks) return [];
        
        return this.tasks.filter(task => {
            // Filter by project
            if (this.filters.project && task.projectId !== this.filters.project) {
                return false;
            }
            
            // Filter by assignee
            if (this.filters.assignee && task.assigneeId !== this.filters.assignee) {
                return false;
            }
            
            // Filter by priority
            if (this.filters.priority && task.priority !== this.filters.priority) {
                return false;
            }
            
            // Filter by due date
            if (this.filters.dueDate) {
                if (!task.dueDate) {
                    return false;
                }
                
                const taskDate = new Date(task.dueDate);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                const tomorrow = new Date(today);
                tomorrow.setDate(tomorrow.getDate() + 1);
                
                const nextWeek = new Date(today);
                nextWeek.setDate(nextWeek.getDate() + 7);
                
                const nextMonth = new Date(today);
                nextMonth.setMonth(nextMonth.getMonth() + 1);
                
                switch (this.filters.dueDate) {
                    case 'today':
                        return taskDate.toDateString() === today.toDateString();
                    case 'tomorrow':
                        return taskDate.toDateString() === tomorrow.toDateString();
                    case 'week':
                        return taskDate >= today && taskDate < nextWeek;
                    case 'month':
                        return taskDate >= today && taskDate < nextMonth;
                    case 'overdue':
                        return taskDate < today;
                    default:
                        return true;
                }
            }
            
            // Filter by search
            if (this.filters.search && this.filters.search.trim() !== '') {
                const searchTerm = this.filters.search.toLowerCase();
                return (
                    task.title.toLowerCase().includes(searchTerm) ||
                    (task.description && task.description.toLowerCase().includes(searchTerm))
                );
            }
            
            return true;
        });
    }
    
    /**
     * Group tasks by their status
     */
    groupTasksByStatus(tasks) {
        const result = {};
        
        this.columns.forEach(column => {
            result[column.id] = [];
        });
        
        tasks.forEach(task => {
            const status = task.status || 'inbox';
            
            if (result[status]) {
                result[status].push(task);
            } else {
                // If status doesn't match any column, put in inbox
                result['inbox'].push(task);
            }
        });
        
        // Sort tasks in each column (newest first by default)
        for (const status in result) {
            result[status].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
        }
        
        return result;
    }
    
    /**
     * Open the task detail modal
     */
    async openTaskDetail(taskId) {
        // Get the task
        const task = await Storage.get('tasks', taskId);
        
        if (!task) {
            Toast.error('Task not found');
            return;
        }
        
        // Show the modal
        const modal = this.find('#task-detail-modal');
        const modalContent = this.find('#task-detail-content');
        
        // Show loading state
        modalContent.innerHTML = `
            <div class="p-6">
                <div class="w-6 h-6 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
            </div>
        `;
        
        modal.classList.remove('hidden');
        
        // Get related data
        let projectName = 'None';
        let projectColor = '#3b82f6';
        if (task.projectId) {
            const project = await Storage.get('projects', task.projectId);
            if (project) {
                projectName = project.name;
                projectColor = project.color || projectColor;
            }
        }
        
        let assigneeName = 'Unassigned';
        let assigneeAvatar = '';
        if (task.assigneeId) {
            const assignee = await Storage.get('users', task.assigneeId);
            if (assignee) {
                assigneeName = assignee.name;
                assigneeAvatar = assignee.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(assignee.name)}&size=32`;
            }
        }
        
        // Format dates
        const createdAt = Helpers.formatDate(task.createdAt, 'long');
        const updatedAt = Helpers.formatDate(task.updatedAt, 'long');
        
        // Due date
        const dueDate = task.dueDate ? Helpers.formatDate(task.dueDate) : 'None';
        const isPastDue = task.dueDate ? Helpers.isPastDue(task.dueDate) : false;
        const dueDateClass = isPastDue ? 'text-red-600 dark:text-red-400' : '';
        
        // Status badge
        const statusLabel = this.getStatusLabel(task.status);
        const statusClass = this.getStatusBadgeClass(task.status);
        
        // Priority badge
        const priorityLabel = Helpers.getPriorityLabel(task.priority);
        const priorityClass = this.getPriorityBadgeClass(task.priority);
        
        // Render task details
        modalContent.innerHTML = `
            <div>
                <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                    <div class="flex justify-between items-start">
                        <h3 class="text-lg font-semibold">${task.title}</h3>
                        <button id="close-detail-btn" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <div class="mt-2 flex flex-wrap gap-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}">
                            ${statusLabel}
                        </span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityClass}">
                            ${priorityLabel}
                        </span>
                    </div>
                </div>
                
                <div class="px-6 py-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Project</h4>
                            <p class="mt-1 flex items-center">
                                <span class="inline-block w-3 h-3 rounded-full mr-2" style="background-color: ${projectColor}"></span>
                                ${projectName}
                            </p>
                        </div>
                        <div>
                            <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Assignee</h4>
                            <p class="mt-1 flex items-center">
                                ${assigneeAvatar ? `<img src="${assigneeAvatar}" alt="${assigneeName}" class="w-5 h-5 rounded-full mr-2">` : ''}
                                ${assigneeName}
                            </p>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Created</h4>
                            <p class="mt-1">${createdAt}</p>
                        </div>
                        <div>
                            <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Updated</h4>
                            <p class="mt-1">${updatedAt}</p>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Due Date</h4>
                        <p class="mt-1 ${dueDateClass}">${dueDate}</p>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Description</h4>
                        <div class="mt-1 prose prose-sm dark:prose-dark max-w-none">
                            ${task.description ? Helpers.markdownToHtml(task.description) : '<p class="text-gray-400 dark:text-gray-500">No description</p>'}
                        </div>
                    </div>
                </div>
                
                <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-between">
                    <button id="delete-task-btn" class="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                        <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                    </button>
                    
                    <div>
                        <button id="edit-task-btn" class="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Set up event listeners
        this.find('#close-detail-btn').addEventListener('click', () => {
            modal.classList.add('hidden');
        });
        
        this.find('#edit-task-btn').addEventListener('click', () => {
            modal.classList.add('hidden');
            this.openEditTaskModal(task);
        });
        
        this.find('#delete-task-btn').addEventListener('click', () => {
            this.confirmDeleteTask(task);
        });
        
        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
    
    /**
     * Open the edit task modal
     */
    async openEditTaskModal(task) {
        // Show the modal
        const modal = this.find('#edit-task-modal');
        const modalContent = this.find('#edit-task-content');
        
        // Show loading state
        modalContent.innerHTML = `
            <div class="p-6">
                <div class="w-6 h-6 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
            </div>
        `;
        
        modal.classList.remove('hidden');
        
        // Load projects for dropdown
        const projects = await Storage.getAll('projects');
        let projectOptions = '<option value="">None</option>';
        
        if (projects.length > 0) {
            // Sort projects by name
            projects.sort((a, b) => a.name.localeCompare(b.name));
            
            projects.forEach(project => {
                const selected = task.projectId === project.id ? 'selected' : '';
                projectOptions += `<option value="${project.id}" ${selected}>${project.name}</option>`;
            });
        }
        
        // Load users for assignee dropdown
        const users = await Storage.getAll('users');
        let assigneeOptions = '<option value="">Unassigned</option>';
        
        if (users.length > 0) {
            // Sort users by name
            users.sort((a, b) => a.name.localeCompare(b.name));
            
            users.forEach(user => {
                const selected = task.assigneeId === user.id ? 'selected' : '';
                assigneeOptions += `<option value="${user.id}" ${selected}>${user.name}</option>`;
            });
        }
        
        // Format due date for input
        const dueDate = task.dueDate ? task.dueDate.split('T')[0] : '';
        
        // Render edit form
        modalContent.innerHTML = `
            <div>
                <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                    <div class="flex justify-between items-start">
                        <h3 class="text-lg font-semibold">Edit Task</h3>
                        <button id="close-edit-btn" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <form id="edit-task-form">
                    <div class="px-6 py-4">
                        <input type="hidden" id="edit-task-id" value="${task.id}">
                        
                        <div class="mb-4">
                            <label for="edit-task-title" class="block text-sm font-medium mb-1">Title</label>
                            <input type="text" id="edit-task-title" class="glass dark:glass-dark w-full rounded-md py-2 px-3" value="${task.title}" required>
                        </div>
                        
                        <div class="mb-4">
                            <label for="edit-task-description" class="block text-sm font-medium mb-1">Description</label>
                            <textarea id="edit-task-description" class="glass dark:glass-dark w-full rounded-md py-2 px-3 h-24">${task.description || ''}</textarea>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label for="edit-task-project" class="block text-sm font-medium mb-1">Project</label>
                                <select id="edit-task-project" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                    ${projectOptions}
                                </select>
                            </div>
                            
                            <div>
                                <label for="edit-task-priority" class="block text-sm font-medium mb-1">Priority</label>
                                <select id="edit-task-priority" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                    <option value="low" ${task.priority === 'low' ? 'selected' : ''}>Low</option>
                                    <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                                    <option value="high" ${task.priority === 'high' ? 'selected' : ''}>High</option>
                                    <option value="urgent" ${task.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label for="edit-task-assignee" class="block text-sm font-medium mb-1">Assign To</label>
                                <select id="edit-task-assignee" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                    ${assigneeOptions}
                                </select>
                            </div>
                            
                            <div>
                                <label for="edit-task-due-date" class="block text-sm font-medium mb-1">Due Date</label>
                                <input type="date" id="edit-task-due-date" class="glass dark:glass-dark w-full rounded-md py-2 px-3" value="${dueDate}">
                            </div>
                        </div>
                        
                        <div>
                            <label for="edit-task-status" class="block text-sm font-medium mb-1">Status</label>
                            <select id="edit-task-status" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                <option value="inbox" ${task.status === 'inbox' ? 'selected' : ''}>Inbox</option>
                                <option value="assigned" ${task.status === 'assigned' ? 'selected' : ''}>Assigned</option>
                                <option value="in-progress" ${task.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
                                <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                        <button type="button" id="cancel-edit-btn" class="mr-3 inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Cancel
                        </button>
                        <button type="submit" id="save-edit-btn" class="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        // Set up event listeners
        this.find('#close-edit-btn').addEventListener('click', () => {
            modal.classList.add('hidden');
        });
        
        this.find('#cancel-edit-btn').addEventListener('click', () => {
            modal.classList.add('hidden');
        });
        
        // Handle form submission
        this.find('#edit-task-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTaskChanges();
        });
        
        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
    
    /**
     * Save task changes from edit form
     */
    async saveTaskChanges() {
        try {
            const taskId = this.find('#edit-task-id').value;
            const title = this.find('#edit-task-title').value.trim();
            const description = this.find('#edit-task-description').value.trim();
            const projectId = this.find('#edit-task-project').value || null;
            const priority = this.find('#edit-task-priority').value;
            const assigneeId = this.find('#edit-task-assignee').value || null;
            const dueDate = this.find('#edit-task-due-date').value || null;
            const status = this.find('#edit-task-status').value;
            
            // Validate title
            if (!title) {
                Toast.error('Title is required');
                return;
            }
            
            // Get the existing task
            const existingTask = await Storage.get('tasks', taskId);
            
            if (!existingTask) {
                Toast.error('Task not found');
                return;
            }
            
            // Update the task
            const updatedTask = {
                ...existingTask,
                title,
                description,
                projectId,
                priority,
                assigneeId,
                dueDate,
                status,
                updatedAt: new Date().toISOString()
            };
            
            await Storage.save('tasks', updatedTask);
            
            // Close the modal
            this.find('#edit-task-modal').classList.add('hidden');
            
            // Refresh tasks
            this.loadTasks();
            
            // Show success message
            Toast.success('Task updated successfully');
            
            // Emit event
            EventBus.emit(Events.TASK_UPDATED, updatedTask);
        } catch (error) {
            console.error('Failed to update task', error);
            Toast.error('Failed to update task. Please try again.');
        }
    }
    
    /**
     * Confirm and delete a task
     */
    confirmDeleteTask(task) {
        Modal.confirm({
            title: 'Delete Task',
            message: `Are you sure you want to delete "${task.title}"? This action cannot be undone.`,
            confirmText: 'Delete',
            cancelText: 'Cancel',
            type: 'danger'
        }).then(async (confirmed) => {
            if (confirmed) {
                try {
                    await Storage.delete('tasks', task.id);
                    
                    // Close the detail modal
                    this.find('#task-detail-modal').classList.add('hidden');
                    
                    // Refresh tasks
                    this.loadTasks();
                    
                    // Show success message
                    Toast.success('Task deleted successfully');
                    
                    // Emit event
                    EventBus.emit(Events.TASK_DELETED, task.id);
                } catch (error) {
                    console.error('Failed to delete task', error);
                    Toast.error('Failed to delete task. Please try again.');
                }
            }
        });
    }
    
    /**
     * Open the new task modal
     */
    openNewTaskModal() {
        // Use the AppShell's new task modal
        const appShell = document.querySelector('[data-component-id]');
        if (appShell && appShell.__component instanceof AppShell) {
            appShell.__component.openNewTaskModal();
        } else {
            Toast.error('Could not open new task modal');
        }
    }
    
    /**
     * Set up drag and drop for task columns
     */
    setupDragAndDrop() {
        // Setup drop zones
        this.columns.forEach(column => {
            const columnElement = this.find(`#${column.id}-tasks`);
            
            // Make column a drop target
            columnElement.addEventListener('dragover', (e) => {
                e.preventDefault();
                columnElement.classList.add('bg-blue-50', 'dark:bg-blue-900', 'bg-opacity-50');
            });
            
            columnElement.addEventListener('dragleave', () => {
                columnElement.classList.remove('bg-blue-50', 'dark:bg-blue-900', 'bg-opacity-50');
            });
            
            columnElement.addEventListener('drop', (e) => {
                e.preventDefault();
                columnElement.classList.remove('bg-blue-50', 'dark:bg-blue-900', 'bg-opacity-50');
                
                // Get the dragged task ID
                const taskId = this.draggedTask;
                
                if (taskId) {
                    this.moveTask(taskId, column.id);
                }
            });
        });
    }
    
    /**
     * Handle drag start event
     */
    handleDragStart(e, taskId) {
        this.draggedTask = taskId;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', taskId);
        e.currentTarget.classList.add('opacity-50');
    }
    
    /**
     * Move a task to a different status column
     */
    async moveTask(taskId, newStatus) {
        try {
            const task = await Storage.get('tasks', taskId);
            
            if (!task) {
                Toast.error('Task not found');
                return;
            }
            
            // Only update if the status actually changed
            if (task.status !== newStatus) {
                const updatedTask = {
                    ...task,
                    status: newStatus,
                    updatedAt: new Date().toISOString()
                };
                
                await Storage.save('tasks', updatedTask);
                
                // Refresh tasks
                this.loadTasks();
                
                // Emit event
                EventBus.emit(Events.TASK_STATUS_CHANGED, {
                    taskId: task.id,
                    newStatus,
                    previousStatus: task.status
                });
            }
        } catch (error) {
            console.error('Failed to move task', error);
            Toast.error('Failed to move task. Please try again.');
        }
    }
    
    /**
     * Get icon HTML for a column
     */
    getColumnIcon(icon) {
        switch (icon) {
            case 'inbox':
                return `
                    <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                `;
            case 'user':
                return `
                    <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                `;
            case 'clock':
                return `
                    <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                `;
            case 'check':
                return `
                    <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                `;
            default:
                return '';
        }
    }
    
    /**
     * Get status label
     */
    getStatusLabel(status) {
        switch (status) {
            case 'inbox':
                return 'Inbox';
            case 'assigned':
                return 'Assigned';
            case 'in-progress':
                return 'In Progress';
            case 'completed':
                return 'Completed';
            default:
                return 'Inbox';
        }
    }
    
    /**
     * Get CSS class for status badge
     */
    getStatusBadgeClass(status) {
        switch (status) {
            case 'inbox':
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
            case 'assigned':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
            case 'in-progress':
                return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
            case 'completed':
                return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            default:
                return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
        }
    }
    
    /**
     * Get CSS class for priority badge
     */
    getPriorityBadgeClass(priority) {
        switch (priority) {
            case 'low':
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
            case 'high':
                return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
            case 'urgent':
                return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            default:
                return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
        }
    }
}

// Register the component globally
window.TaskBoard = TaskBoard;