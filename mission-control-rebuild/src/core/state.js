/**
 * State Management System for the Mission Control Dashboard
 * Provides a central store for application state with reactivity
 */

const State = (function() {
    // Private state container
    let _state = {};
    
    // Subscribers for state changes
    const _subscribers = {};
    
    // History for undo/redo functionality
    const _history = [];
    let _historyIndex = -1;
    const _maxHistorySize = 50;
    
    return {
        /**
         * Initialize the state with default values
         * @param {Object} initialState - Initial state object
         */
        init(initialState = {}) {
            _state = { ...initialState };
            
            // Add some default state properties
            _state.app = _state.app || {
                isInitialized: false,
                isLoading: true,
                currentView: 'dashboard',
                sidebarOpen: true,
                modals: {
                    taskCreate: false,
                    taskEdit: false,
                    projectCreate: false,
                    settings: false,
                }
            };
            
            _state.tasks = _state.tasks || {
                items: [],
                loading: false,
                error: null,
                filters: {
                    status: null,
                    priority: null,
                    assignee: null,
                    project: null,
                    search: '',
                    dueDate: null
                },
                currentTask: null
            };
            
            _state.projects = _state.projects || {
                items: [],
                loading: false,
                error: null,
                currentProject: null
            };
            
            _state.users = _state.users || {
                items: [],
                loading: false,
                error: null,
                currentUser: null
            };
        },
        
        /**
         * Get the current state
         * @param {string} [path] - Optional dot notation path to a specific state property
         * @returns {*} The requested state or entire state object
         */
        get(path) {
            if (!path) {
                return Helpers.deepClone(_state);
            }
            
            // Handle dot notation for nested properties
            const props = path.split('.');
            let result = _state;
            
            for (const prop of props) {
                if (result === undefined || result === null) {
                    return undefined;
                }
                result = result[prop];
            }
            
            return Helpers.deepClone(result);
        },
        
        /**
         * Set a state property
         * @param {string} path - Dot notation path to the property
         * @param {*} value - New value
         * @param {boolean} [recordHistory=true] - Whether to record this change in history
         */
        set(path, value, recordHistory = true) {
            // Clone current state for history if needed
            if (recordHistory) {
                // Truncate history if we're not at the end
                if (_historyIndex < _history.length - 1) {
                    _history.splice(_historyIndex + 1);
                }
                
                // Add current state to history
                _history.push(Helpers.deepClone(_state));
                _historyIndex = _history.length - 1;
                
                // Limit history size
                if (_history.length > _maxHistorySize) {
                    _history.shift();
                    _historyIndex--;
                }
            }
            
            // Handle dot notation
            const props = path.split('.');
            let current = _state;
            
            for (let i = 0; i < props.length - 1; i++) {
                const prop = props[i];
                
                // Create the property if it doesn't exist
                if (!current[prop]) {
                    current[prop] = {};
                }
                
                current = current[prop];
            }
            
            // Set the value
            const lastProp = props[props.length - 1];
            current[lastProp] = value;
            
            // Notify subscribers
            this._notifySubscribers(path);
        },
        
        /**
         * Subscribe to changes in a state property
         * @param {string} path - Dot notation path to the property
         * @param {Function} callback - Function to call when the property changes
         * @returns {Function} Unsubscribe function
         */
        subscribe(path, callback) {
            if (!_subscribers[path]) {
                _subscribers[path] = [];
            }
            
            _subscribers[path].push(callback);
            
            return () => {
                _subscribers[path] = _subscribers[path].filter(cb => cb !== callback);
                
                if (_subscribers[path].length === 0) {
                    delete _subscribers[path];
                }
            };
        },
        
        /**
         * Notify subscribers of state changes
         * @param {string} path - Path that was changed
         * @private
         */
        _notifySubscribers(path) {
            // Notify subscribers to the exact path
            if (_subscribers[path]) {
                _subscribers[path].forEach(callback => {
                    callback(this.get(path));
                });
            }
            
            // Notify subscribers to parent paths
            const parts = path.split('.');
            for (let i = parts.length - 1; i > 0; i--) {
                const parentPath = parts.slice(0, i).join('.');
                if (_subscribers[parentPath]) {
                    _subscribers[parentPath].forEach(callback => {
                        callback(this.get(parentPath));
                    });
                }
            }
            
            // Notify subscribers to the entire state
            if (_subscribers['*']) {
                _subscribers['*'].forEach(callback => {
                    callback(this.get());
                });
            }
        },
        
        /**
         * Undo the last state change
         * @returns {boolean} Whether the operation was successful
         */
        undo() {
            if (_historyIndex > 0) {
                _historyIndex--;
                _state = Helpers.deepClone(_history[_historyIndex]);
                this._notifySubscribers('*');
                return true;
            }
            return false;
        },
        
        /**
         * Redo a previously undone state change
         * @returns {boolean} Whether the operation was successful
         */
        redo() {
            if (_historyIndex < _history.length - 1) {
                _historyIndex++;
                _state = Helpers.deepClone(_history[_historyIndex]);
                this._notifySubscribers('*');
                return true;
            }
            return false;
        },
        
        /**
         * Reset the state to its initial values
         * @param {Object} [initialState] - Optional new initial state
         */
        reset(initialState) {
            this.init(initialState);
            _history.length = 0;
            _historyIndex = -1;
            this._notifySubscribers('*');
        }
    };
})();