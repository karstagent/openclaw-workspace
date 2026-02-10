/**
 * Helper utilities for the Mission Control Dashboard
 */

const Helpers = {
    /**
     * Generate a unique ID
     * @returns {string} Unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substring(2);
    },
    
    /**
     * Format a date for display
     * @param {string} dateString - ISO date string
     * @param {string} format - Format to use (short, medium, long)
     * @returns {string} Formatted date
     */
    formatDate(dateString, format = 'medium') {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
            return 'Invalid date';
        }
        
        switch (format) {
            case 'short':
                return date.toLocaleDateString();
            case 'long':
                return date.toLocaleString();
            case 'time':
                return date.toLocaleTimeString();
            case 'medium':
            default:
                return date.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
        }
    },
    
    /**
     * Format relative time (e.g., 2 days ago)
     * @param {string} dateString - ISO date string
     * @returns {string} Relative time
     */
    formatRelativeTime(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        
        if (isNaN(date.getTime())) {
            return 'Invalid date';
        }
        
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return `${diffInSeconds} second${diffInSeconds !== 1 ? 's' : ''} ago`;
        }
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
            return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
        }
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) {
            return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
        }
        
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays < 30) {
            return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
        }
        
        const diffInMonths = Math.floor(diffInDays / 30);
        if (diffInMonths < 12) {
            return `${diffInMonths} month${diffInMonths !== 1 ? 's' : ''} ago`;
        }
        
        const diffInYears = Math.floor(diffInMonths / 12);
        return `${diffInYears} year${diffInYears !== 1 ? 's' : ''} ago`;
    },
    
    /**
     * Create a debounced function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Milliseconds to wait
     * @returns {Function} Debounced function
     */
    debounce(func, wait = 300) {
        let timeout;
        
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Create a throttled function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Throttle time in milliseconds
     * @returns {Function} Throttled function
     */
    throttle(func, limit = 300) {
        let inThrottle;
        
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Deep clone an object
     * @param {Object} obj - Object to clone
     * @returns {Object} Cloned object
     */
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    
    /**
     * Get priority color class
     * @param {string} priority - Priority level (low, medium, high, urgent)
     * @returns {string} CSS class name
     */
    getPriorityClass(priority) {
        switch (priority) {
            case 'low':
                return 'priority-low';
            case 'medium':
                return 'priority-medium';
            case 'high':
                return 'priority-high';
            case 'urgent':
                return 'priority-urgent';
            default:
                return 'priority-medium';
        }
    },
    
    /**
     * Get status color class
     * @param {string} status - Status (pending, in-progress, review, completed)
     * @returns {string} CSS class name
     */
    getStatusClass(status) {
        switch (status) {
            case 'pending':
            case 'inbox':
                return 'status-pending';
            case 'in-progress':
            case 'assigned':
                return 'status-in-progress';
            case 'review':
                return 'status-review';
            case 'completed':
                return 'status-completed';
            default:
                return 'status-pending';
        }
    },
    
    /**
     * Get priority label
     * @param {string} priority - Priority level (low, medium, high, urgent)
     * @returns {string} Human-friendly label
     */
    getPriorityLabel(priority) {
        switch (priority) {
            case 'low':
                return 'Low Priority';
            case 'medium':
                return 'Medium Priority';
            case 'high':
                return 'High Priority';
            case 'urgent':
                return 'Urgent Priority';
            default:
                return 'Medium Priority';
        }
    },
    
    /**
     * Get status label
     * @param {string} status - Status (pending, in-progress, review, completed)
     * @returns {string} Human-friendly label
     */
    getStatusLabel(status) {
        switch (status) {
            case 'pending':
            case 'inbox':
                return 'Pending';
            case 'in-progress':
                return 'In Progress';
            case 'assigned':
                return 'Assigned';
            case 'review':
                return 'In Review';
            case 'completed':
                return 'Completed';
            default:
                return 'Pending';
        }
    },
    
    /**
     * Convert HTML special characters to entities
     * @param {string} str - String to escape
     * @returns {string} Escaped string
     */
    escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },
    
    /**
     * Format a markdown string to HTML
     * @param {string} markdown - Markdown text
     * @returns {string} HTML
     */
    markdownToHtml(markdown) {
        if (!markdown) return '';
        return marked.parse(markdown);
    },
    
    /**
     * Extract data from a form
     * @param {HTMLFormElement} form - Form element
     * @returns {Object} Form data
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    },
    
    /**
     * Check if a date is past due
     * @param {string} dateString - ISO date string
     * @returns {boolean} True if the date is in the past
     */
    isPastDue(dateString) {
        if (!dateString) return false;
        
        const date = new Date(dateString);
        const now = new Date();
        
        if (isNaN(date.getTime())) {
            return false;
        }
        
        // Set times to midnight to compare only dates
        date.setHours(0, 0, 0, 0);
        now.setHours(0, 0, 0, 0);
        
        return date < now;
    },
    
    /**
     * Get days until a date
     * @param {string} dateString - ISO date string
     * @returns {number} Days until the date (negative if past)
     */
    daysUntil(dateString) {
        if (!dateString) return null;
        
        const date = new Date(dateString);
        const now = new Date();
        
        if (isNaN(date.getTime())) {
            return null;
        }
        
        // Set times to midnight to compare only dates
        date.setHours(0, 0, 0, 0);
        now.setHours(0, 0, 0, 0);
        
        const diffInTime = date.getTime() - now.getTime();
        return Math.round(diffInTime / (1000 * 3600 * 24));
    },
    
    /**
     * Format a due date with friendly text
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date string
     */
    formatDueDate(dateString) {
        if (!dateString) return 'No due date';
        
        const days = this.daysUntil(dateString);
        
        if (days === null) {
            return 'Invalid date';
        }
        
        if (days < 0) {
            return `Overdue by ${Math.abs(days)} day${Math.abs(days) !== 1 ? 's' : ''}`;
        }
        
        if (days === 0) {
            return 'Due today';
        }
        
        if (days === 1) {
            return 'Due tomorrow';
        }
        
        if (days < 7) {
            return `Due in ${days} days`;
        }
        
        return this.formatDate(dateString);
    }
};