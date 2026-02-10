/**
 * Event Bus for the Mission Control Dashboard
 * Provides a pub/sub system for communication between components
 */

const EventBus = {
    events: {},
    
    /**
     * Subscribe to an event
     * @param {string} eventName - Name of the event
     * @param {Function} callback - Function to call when the event is emitted
     * @returns {Function} Unsubscribe function
     */
    subscribe(eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        
        this.events[eventName].push(callback);
        
        // Return unsubscribe function
        return () => {
            this.events[eventName] = this.events[eventName].filter(
                cb => cb !== callback
            );
        };
    },
    
    /**
     * Emit an event
     * @param {string} eventName - Name of the event
     * @param {*} data - Data to pass to the event handlers
     */
    emit(eventName, data) {
        if (this.events[eventName]) {
            this.events[eventName].forEach(callback => {
                callback(data);
            });
        }
    },
    
    /**
     * Subscribe to an event and unsubscribe after it's emitted once
     * @param {string} eventName - Name of the event
     * @param {Function} callback - Function to call when the event is emitted
     * @returns {Function} Unsubscribe function
     */
    once(eventName, callback) {
        const unsubscribe = this.subscribe(eventName, (data) => {
            unsubscribe();
            callback(data);
        });
        
        return unsubscribe;
    },
    
    /**
     * Remove all subscriptions for an event
     * @param {string} eventName - Name of the event
     */
    clear(eventName) {
        if (eventName) {
            delete this.events[eventName];
        } else {
            this.events = {};
        }
    }
};

// Standard events used across the application
const Events = {
    // Task events
    TASK_CREATED: 'task:created',
    TASK_UPDATED: 'task:updated',
    TASK_DELETED: 'task:deleted',
    TASK_STATUS_CHANGED: 'task:statusChanged',
    TASK_ASSIGNMENT_CHANGED: 'task:assignmentChanged',
    
    // Project events
    PROJECT_CREATED: 'project:created',
    PROJECT_UPDATED: 'project:updated',
    PROJECT_DELETED: 'project:deleted',
    
    // User events
    USER_UPDATED: 'user:updated',
    
    // UI events
    MODAL_OPEN: 'ui:modalOpen',
    MODAL_CLOSE: 'ui:modalClose',
    ROUTE_CHANGE: 'route:change',
    
    // System events
    APP_INITIALIZED: 'system:initialized',
    DATA_LOADED: 'system:dataLoaded',
    ERROR: 'system:error',
    
    // Filter events
    FILTER_CHANGED: 'filter:changed'
};