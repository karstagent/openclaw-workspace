/**
 * Storage utility for Mission Control Dashboard
 * Handles persistent storage of all application data using IndexedDB
 */

// Use localForage for IndexedDB with a simple API
const Storage = {
    // Database instances for different data types
    taskStore: localforage.createInstance({
        name: 'MissionControl',
        storeName: 'tasks'
    }),
    
    projectStore: localforage.createInstance({
        name: 'MissionControl',
        storeName: 'projects'
    }),
    
    userStore: localforage.createInstance({
        name: 'MissionControl',
        storeName: 'users'
    }),
    
    settingsStore: localforage.createInstance({
        name: 'MissionControl',
        storeName: 'settings'
    }),
    
    /**
     * Initialize the storage system
     */
    async init() {
        try {
            // Ensure all stores are ready
            await Promise.all([
                this.taskStore.ready(),
                this.projectStore.ready(),
                this.userStore.ready(),
                this.settingsStore.ready()
            ]);
            
            // Check if we need to add initial data
            const hasInitialData = await this.settingsStore.getItem('initialDataLoaded');
            
            if (!hasInitialData) {
                await this.loadInitialData();
            }
            
            console.log('Storage initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize storage', error);
            return false;
        }
    },
    
    /**
     * Load initial data into the stores
     */
    async loadInitialData() {
        try {
            // Add default users
            await this.userStore.setItem('current-user', {
                id: 'current-user',
                name: 'Jordan',
                role: 'admin',
                avatar: 'https://ui-avatars.com/api/?name=Jordan&background=random'
            });
            
            await this.userStore.setItem('pip', {
                id: 'pip',
                name: 'Pip',
                role: 'assistant',
                avatar: 'https://ui-avatars.com/api/?name=Pip&background=0D8ABC'
            });
            
            // Add default projects
            await this.projectStore.setItem('project-1', {
                id: 'project-1',
                name: 'GlassWall',
                description: 'Platform for agent communities with two-tier messaging',
                color: '#3b82f6',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
            
            await this.projectStore.setItem('project-2', {
                id: 'project-2',
                name: 'Command Station',
                description: 'System monitoring and management dashboard',
                color: '#8b5cf6',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
            
            // Add default tasks
            await this.taskStore.setItem('task-1', {
                id: 'task-1',
                title: 'Improve UI design for Mission Control',
                description: 'Implement a modernized UI with enhanced user experience for the Mission Control dashboard.',
                status: 'in-progress',
                priority: 'high',
                projectId: 'project-1',
                assigneeId: 'pip',
                dueDate: this.addDays(new Date(), 2).toISOString(),
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
            
            await this.taskStore.setItem('task-2', {
                id: 'task-2',
                title: 'Implement drag-and-drop functionality',
                description: 'Add the ability to drag tasks between columns for easier status updates.',
                status: 'pending',
                priority: 'medium',
                projectId: 'project-1',
                assigneeId: 'pip',
                tags: ['frontend', 'UX'],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
            
            // Set the flag indicating initial data is loaded
            await this.settingsStore.setItem('initialDataLoaded', true);
            
            console.log('Initial data loaded successfully');
            return true;
        } catch (error) {
            console.error('Failed to load initial data', error);
            return false;
        }
    },
    
    /**
     * Helper method to add days to a date
     * @param {Date} date - The starting date
     * @param {number} days - Number of days to add
     * @returns {Date} The new date
     */
    addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },
    
    /**
     * Get all items from a store
     * @param {string} storeName - Name of the store to query ('tasks', 'projects', 'users', 'settings')
     * @returns {Promise<Array>} Array of items
     */
    async getAll(storeName) {
        try {
            const store = this[`${storeName}Store`];
            
            if (!store) {
                throw new Error(`Store '${storeName}' doesn't exist`);
            }
            
            const items = [];
            
            await store.iterate((value) => {
                items.push(value);
            });
            
            return items;
        } catch (error) {
            console.error(`Failed to get all items from ${storeName}`, error);
            return [];
        }
    },
    
    /**
     * Get a specific item by id
     * @param {string} storeName - Name of the store
     * @param {string} id - Item id
     * @returns {Promise<Object|null>} The requested item or null
     */
    async get(storeName, id) {
        try {
            const store = this[`${storeName}Store`];
            
            if (!store) {
                throw new Error(`Store '${storeName}' doesn't exist`);
            }
            
            return await store.getItem(id);
        } catch (error) {
            console.error(`Failed to get item ${id} from ${storeName}`, error);
            return null;
        }
    },
    
    /**
     * Save an item to a store
     * @param {string} storeName - Name of the store
     * @param {Object} item - The item to save (must have an id property)
     * @returns {Promise<boolean>} Success or failure
     */
    async save(storeName, item) {
        try {
            if (!item.id) {
                throw new Error('Item must have an id property');
            }
            
            const store = this[`${storeName}Store`];
            
            if (!store) {
                throw new Error(`Store '${storeName}' doesn't exist`);
            }
            
            // Update timestamp
            item.updatedAt = new Date().toISOString();
            
            // Add createdAt if it's a new item
            if (!item.createdAt) {
                item.createdAt = new Date().toISOString();
            }
            
            await store.setItem(item.id, item);
            return true;
        } catch (error) {
            console.error(`Failed to save item to ${storeName}`, error);
            return false;
        }
    },
    
    /**
     * Delete an item from a store
     * @param {string} storeName - Name of the store
     * @param {string} id - Item id to delete
     * @returns {Promise<boolean>} Success or failure
     */
    async delete(storeName, id) {
        try {
            const store = this[`${storeName}Store`];
            
            if (!store) {
                throw new Error(`Store '${storeName}' doesn't exist`);
            }
            
            await store.removeItem(id);
            return true;
        } catch (error) {
            console.error(`Failed to delete item ${id} from ${storeName}`, error);
            return false;
        }
    },
    
    /**
     * Query items from a store with filters
     * @param {string} storeName - Name of the store
     * @param {Function} filterFn - Filter function (item => boolean)
     * @returns {Promise<Array>} Filtered array of items
     */
    async query(storeName, filterFn) {
        try {
            const items = await this.getAll(storeName);
            return items.filter(filterFn);
        } catch (error) {
            console.error(`Failed to query items from ${storeName}`, error);
            return [];
        }
    },
    
    /**
     * Create a backup of all data
     * @returns {Promise<Object>} Backup data object
     */
    async createBackup() {
        try {
            const backup = {
                tasks: await this.getAll('tasks'),
                projects: await this.getAll('projects'),
                users: await this.getAll('users'),
                settings: await this.getAll('settings'),
                timestamp: new Date().toISOString()
            };
            
            return backup;
        } catch (error) {
            console.error('Failed to create backup', error);
            return null;
        }
    },
    
    /**
     * Restore data from a backup
     * @param {Object} backup - Backup data object
     * @returns {Promise<boolean>} Success or failure
     */
    async restoreBackup(backup) {
        try {
            // Validate backup
            if (!backup || !backup.tasks || !backup.projects || !backup.users || !backup.settings) {
                throw new Error('Invalid backup data');
            }
            
            // Clear all stores
            await Promise.all([
                this.taskStore.clear(),
                this.projectStore.clear(),
                this.userStore.clear(),
                this.settingsStore.clear()
            ]);
            
            // Restore tasks
            for (const task of backup.tasks) {
                await this.taskStore.setItem(task.id, task);
            }
            
            // Restore projects
            for (const project of backup.projects) {
                await this.projectStore.setItem(project.id, project);
            }
            
            // Restore users
            for (const user of backup.users) {
                await this.userStore.setItem(user.id, user);
            }
            
            // Restore settings
            for (const setting of backup.settings) {
                await this.settingsStore.setItem(setting.id, setting);
            }
            
            return true;
        } catch (error) {
            console.error('Failed to restore backup', error);
            return false;
        }
    }
};