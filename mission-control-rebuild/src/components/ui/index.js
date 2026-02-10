/**
 * UI Component Library for Mission Control Dashboard
 * Collection of reusable UI components
 */

/**
 * Button Component
 */
class Button extends Component {
    init() {
        super.init();
        
        // Default options
        this.text = this.options.text || 'Button';
        this.icon = this.options.icon || null;
        this.type = this.options.type || 'primary';
        this.size = this.options.size || 'md';
        this.onClick = this.options.onClick || null;
    }
    
    render() {
        // Button classes based on type
        const typeClasses = {
            primary: 'bg-blue-600 hover:bg-blue-700 text-white',
            secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white',
            success: 'bg-green-600 hover:bg-green-700 text-white',
            danger: 'bg-red-600 hover:bg-red-700 text-white',
            warning: 'bg-yellow-500 hover:bg-yellow-600 text-white',
            info: 'bg-indigo-600 hover:bg-indigo-700 text-white',
            link: 'bg-transparent hover:underline text-blue-600 dark:text-blue-400'
        };
        
        // Button sizes
        const sizeClasses = {
            sm: 'text-sm py-1 px-2',
            md: 'py-2 px-4',
            lg: 'text-lg py-3 px-6'
        };
        
        // Base classes
        let classes = 'rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';
        
        // Add type and size classes
        classes += ` ${typeClasses[this.type] || typeClasses.primary}`;
        classes += ` ${sizeClasses[this.size] || sizeClasses.md}`;
        
        // Add custom classes
        if (this.options.className) {
            classes += ` ${this.options.className}`;
        }
        
        // Icon HTML if provided
        let iconHtml = '';
        if (this.icon) {
            iconHtml = `<span class="mr-2">${this.icon}</span>`;
        }
        
        this.el.innerHTML = `
            <button type="button" class="${classes}">
                ${iconHtml}${this.text}
            </button>
        `;
    }
    
    setupEvents() {
        if (this.onClick) {
            this.on('button', 'click', this.onClick);
        }
    }
}

/**
 * Card Component
 */
class Card extends Component {
    init() {
        super.init();
        
        this.title = this.options.title || '';
        this.content = this.options.content || '';
        this.footer = this.options.footer || '';
        this.glass = this.options.glass !== false;
    }
    
    render() {
        // Base classes
        let classes = 'rounded-lg overflow-hidden shadow';
        
        // Add glass effect if enabled
        if (this.glass) {
            classes += ' glass dark:glass-dark';
        } else {
            classes += ' bg-white dark:bg-gray-800';
        }
        
        // Add custom classes
        if (this.options.className) {
            classes += ` ${this.options.className}`;
        }
        
        // Card template
        let template = `<div class="${classes}">`;
        
        // Card header if title is provided
        if (this.title) {
            template += `
                <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-lg font-medium">${this.title}</h3>
                </div>
            `;
        }
        
        // Card body
        template += `
            <div class="p-4">
                ${this.content}
            </div>
        `;
        
        // Card footer if provided
        if (this.footer) {
            template += `
                <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    ${this.footer}
                </div>
            `;
        }
        
        template += '</div>';
        
        this.el.innerHTML = template;
    }
}

/**
 * Alert Component
 */
class Alert extends Component {
    init() {
        super.init();
        
        this.type = this.options.type || 'info';
        this.message = this.options.message || '';
        this.dismissible = this.options.dismissible !== false;
        this.icon = this.options.icon || true;
    }
    
    render() {
        // Alert types and their corresponding classes
        const typeClasses = {
            info: 'bg-blue-100 border-blue-500 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            success: 'bg-green-100 border-green-500 text-green-800 dark:bg-green-900 dark:text-green-200',
            warning: 'bg-yellow-100 border-yellow-500 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            error: 'bg-red-100 border-red-500 text-red-800 dark:bg-red-900 dark:text-red-200'
        };
        
        // Icons for each type
        const icons = {
            info: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            success: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            warning: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>',
            error: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
        };
        
        // Base classes
        const classes = `rounded-lg border-l-4 p-4 ${typeClasses[this.type] || typeClasses.info}`;
        
        // Alert template
        let template = `<div class="${classes} flex">`;
        
        // Add icon if enabled
        if (this.icon) {
            template += `
                <div class="flex-shrink-0 mr-3">
                    ${icons[this.type] || icons.info}
                </div>
            `;
        }
        
        // Alert content
        template += `
            <div class="flex-grow">
                ${this.message}
            </div>
        `;
        
        // Add dismiss button if enabled
        if (this.dismissible) {
            template += `
                <div class="flex-shrink-0 ml-3">
                    <button type="button" class="dismiss-btn">
                        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            `;
        }
        
        template += '</div>';
        
        this.el.innerHTML = template;
    }
    
    setupEvents() {
        if (this.dismissible) {
            this.on('.dismiss-btn', 'click', () => {
                this.el.remove();
            });
        }
    }
}

/**
 * Badge Component
 */
class Badge extends Component {
    init() {
        super.init();
        
        this.text = this.options.text || '';
        this.type = this.options.type || 'default';
        this.size = this.options.size || 'md';
    }
    
    render() {
        // Badge types
        const typeClasses = {
            default: 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
            primary: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            danger: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
            info: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
        };
        
        // Badge sizes
        const sizeClasses = {
            sm: 'text-xs px-1.5 py-0.5',
            md: 'text-sm px-2 py-1',
            lg: 'text-base px-2.5 py-1.5'
        };
        
        // Base classes
        let classes = 'inline-block rounded-full font-medium';
        
        // Add type and size classes
        classes += ` ${typeClasses[this.type] || typeClasses.default}`;
        classes += ` ${sizeClasses[this.size] || sizeClasses.md}`;
        
        // Add custom classes
        if (this.options.className) {
            classes += ` ${this.options.className}`;
        }
        
        this.el.innerHTML = `
            <span class="${classes}">
                ${this.text}
            </span>
        `;
    }
}

/**
 * Avatar Component
 */
class Avatar extends Component {
    init() {
        super.init();
        
        this.src = this.options.src || '';
        this.name = this.options.name || '';
        this.size = this.options.size || 'md';
        this.shape = this.options.shape || 'circle';
        this.status = this.options.status || null;
    }
    
    render() {
        // Avatar sizes
        const sizeClasses = {
            xs: 'w-6 h-6 text-xs',
            sm: 'w-8 h-8 text-sm',
            md: 'w-10 h-10 text-base',
            lg: 'w-12 h-12 text-lg',
            xl: 'w-16 h-16 text-xl'
        };
        
        // Avatar shapes
        const shapeClasses = {
            circle: 'rounded-full',
            square: 'rounded-md'
        };
        
        // Base classes
        let classes = 'inline-flex items-center justify-center relative';
        
        // Add size and shape classes
        classes += ` ${sizeClasses[this.size] || sizeClasses.md}`;
        classes += ` ${shapeClasses[this.shape] || shapeClasses.circle}`;
        
        // Add custom classes
        if (this.options.className) {
            classes += ` ${this.options.className}`;
        }
        
        let template = '';
        
        // Image avatar
        if (this.src) {
            template = `
                <div class="${classes} bg-gray-200 dark:bg-gray-700 overflow-hidden">
                    <img src="${this.src}" alt="${this.name}" class="w-full h-full object-cover" />
                </div>
            `;
        }
        // Initials avatar
        else if (this.name) {
            const initials = this.getInitials(this.name);
            const backgroundColor = this.getRandomColor(this.name);
            
            template = `
                <div class="${classes}" style="background-color: ${backgroundColor}; color: white;">
                    ${initials}
                </div>
            `;
        }
        // Placeholder avatar
        else {
            template = `
                <div class="${classes} bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400">
                    <svg class="w-1/2 h-1/2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                </div>
            `;
        }
        
        // Add status indicator if provided
        if (this.status) {
            const statusColors = {
                online: 'bg-green-500',
                away: 'bg-yellow-500',
                busy: 'bg-red-500',
                offline: 'bg-gray-500'
            };
            
            const statusClass = statusColors[this.status] || statusColors.offline;
            
            // Add status dot
            template = template.replace('</div>', `
                <span class="absolute bottom-0 right-0 block rounded-full ring-2 ring-white dark:ring-gray-800 ${statusClass}" style="width: 25%; height: 25%;"></span>
                </div>
            `);
        }
        
        this.el.innerHTML = template;
    }
    
    /**
     * Get initials from a name
     * @param {string} name - Full name
     * @returns {string} Initials (up to 2 characters)
     */
    getInitials(name) {
        const names = name.split(' ');
        
        if (names.length === 1) {
            return names[0].charAt(0).toUpperCase();
        }
        
        return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
    }
    
    /**
     * Generate a random color from a string
     * @param {string} str - String to generate color from
     * @returns {string} Hex color
     */
    getRandomColor(str) {
        // List of colors
        const colors = [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#0ea5e9'
        ];
        
        // Generate a number from the string
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        // Use the hash to pick a color
        return colors[Math.abs(hash) % colors.length];
    }
}

/**
 * Dropdown Component
 */
class Dropdown extends Component {
    init() {
        super.init();
        
        this.trigger = this.options.trigger || 'click';
        this.placement = this.options.placement || 'bottom';
        this.items = this.options.items || [];
        this.label = this.options.label || 'Dropdown';
        this.icon = this.options.icon || null;
    }
    
    render() {
        // Button classes
        const buttonClasses = 'flex items-center justify-between rounded bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500';
        
        // Icon for the dropdown button
        const iconHtml = this.icon ? this.icon : `
            <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
        `;
        
        // Menu placement classes
        const placementClasses = {
            top: 'bottom-full mb-1',
            bottom: 'top-full mt-1',
            left: 'right-full mr-1',
            right: 'left-full ml-1'
        };
        
        // Create the dropdown items
        let itemsHtml = '';
        this.items.forEach((item, index) => {
            if (item.divider) {
                itemsHtml += '<div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>';
            } else {
                const itemClasses = 'block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white';
                itemsHtml += `
                    <a href="${item.href || '#'}" class="${itemClasses}" data-index="${index}">
                        ${item.icon ? `<span class="mr-2">${item.icon}</span>` : ''}
                        ${item.text}
                    </a>
                `;
            }
        });
        
        this.el.innerHTML = `
            <div class="relative">
                <button type="button" class="${buttonClasses} dropdown-toggle">
                    <span>${this.label}</span>
                    ${iconHtml}
                </button>
                
                <div class="dropdown-menu absolute z-10 ${placementClasses[this.placement] || placementClasses.bottom} w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 hidden">
                    <div class="py-1">
                        ${itemsHtml}
                    </div>
                </div>
            </div>
        `;
    }
    
    setupEvents() {
        const toggleButton = this.find('.dropdown-toggle');
        const menu = this.find('.dropdown-menu');
        
        if (this.trigger === 'click') {
            toggleButton.addEventListener('click', () => {
                menu.classList.toggle('hidden');
            });
            
            // Close when clicking outside
            document.addEventListener('click', (event) => {
                if (!this.el.contains(event.target)) {
                    menu.classList.add('hidden');
                }
            });
        } else if (this.trigger === 'hover') {
            this.el.addEventListener('mouseenter', () => {
                menu.classList.remove('hidden');
            });
            
            this.el.addEventListener('mouseleave', () => {
                menu.classList.add('hidden');
            });
        }
        
        // Item click handler
        this.on('.dropdown-menu a', 'click', (event) => {
            const index = parseInt(event.currentTarget.dataset.index, 10);
            const item = this.items[index];
            
            if (item && item.onClick) {
                event.preventDefault();
                item.onClick(item);
            }
            
            // Close the menu after click
            menu.classList.add('hidden');
        });
    }
}

/**
 * Toast Component
 */
class Toast {
    /**
     * Show a toast notification
     * @param {Object} options - Toast options
     * @returns {Object} Toast instance
     */
    static show(options) {
        const {
            message = '',
            type = 'info',
            duration = 3000,
            position = 'top-right',
            onClose = null
        } = options;
        
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed z-50 p-4 space-y-3';
            
            // Position classes
            const positionClasses = {
                'top-right': 'top-0 right-0',
                'top-left': 'top-0 left-0',
                'bottom-right': 'bottom-0 right-0',
                'bottom-left': 'bottom-0 left-0',
                'top-center': 'top-0 left-1/2 transform -translate-x-1/2',
                'bottom-center': 'bottom-0 left-1/2 transform -translate-x-1/2'
            };
            
            container.classList.add(...(positionClasses[position] || positionClasses['top-right']).split(' '));
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        const toastId = `toast-${Date.now()}`;
        toast.id = toastId;
        
        // Toast types
        const typeClasses = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            warning: 'bg-yellow-500',
            error: 'bg-red-500'
        };
        
        // Toast icons
        const icons = {
            info: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            success: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            warning: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>',
            error: '<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
        };
        
        // Create toast content
        toast.innerHTML = `
            <div class="glass dark:glass-dark rounded-lg shadow-lg overflow-hidden max-w-xs transform transition-all duration-300 translate-x-full opacity-0">
                <div class="${typeClasses[type] || typeClasses.info} text-white px-4 py-2 flex justify-between items-center">
                    <div class="flex items-center">
                        ${icons[type] || icons.info}
                        <span class="ml-2 font-medium">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                    </div>
                    <button type="button" class="toast-close focus:outline-none">
                        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <div class="px-4 py-3 bg-white dark:bg-gray-800">
                    ${message}
                </div>
            </div>
        `;
        
        // Add toast to container
        container.appendChild(toast);
        
        // Show toast with animation
        setTimeout(() => {
            const toastEl = toast.querySelector('div');
            toastEl.classList.remove('translate-x-full', 'opacity-0');
        }, 10);
        
        // Close toast handler
        const close = () => {
            const toastEl = toast.querySelector('div');
            toastEl.classList.add('translate-x-full', 'opacity-0');
            
            // Remove after animation
            setTimeout(() => {
                toast.remove();
                
                // Call close callback if provided
                if (onClose) {
                    onClose();
                }
                
                // Remove container if empty
                if (container.children.length === 0) {
                    container.remove();
                }
            }, 300);
        };
        
        // Close button click handler
        toast.querySelector('.toast-close').addEventListener('click', close);
        
        // Auto close after duration
        if (duration > 0) {
            setTimeout(close, duration);
        }
        
        // Return an object to control the toast
        return {
            id: toastId,
            close
        };
    }
    
    /**
     * Show an info toast
     * @param {string} message - Toast message
     * @param {Object} options - Toast options
     * @returns {Object} Toast instance
     */
    static info(message, options = {}) {
        return this.show({ message, type: 'info', ...options });
    }
    
    /**
     * Show a success toast
     * @param {string} message - Toast message
     * @param {Object} options - Toast options
     * @returns {Object} Toast instance
     */
    static success(message, options = {}) {
        return this.show({ message, type: 'success', ...options });
    }
    
    /**
     * Show a warning toast
     * @param {string} message - Toast message
     * @param {Object} options - Toast options
     * @returns {Object} Toast instance
     */
    static warning(message, options = {}) {
        return this.show({ message, type: 'warning', ...options });
    }
    
    /**
     * Show an error toast
     * @param {string} message - Toast message
     * @param {Object} options - Toast options
     * @returns {Object} Toast instance
     */
    static error(message, options = {}) {
        return this.show({ message, type: 'error', ...options });
    }
}

/**
 * Modal Dialog Factory
 */
class Modal {
    /**
     * Show a confirmation dialog
     * @param {Object} options - Dialog options
     * @returns {Promise} Promise that resolves with the result
     */
    static confirm(options) {
        const {
            title = 'Confirm',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'primary',
            icon = null
        } = options;
        
        return new Promise((resolve) => {
            // Create modal container if it doesn't exist
            let container = document.getElementById('modal-container');
            
            if (!container) {
                container = document.createElement('div');
                container.id = 'modal-container';
                document.body.appendChild(container);
            }
            
            // Create modal element
            const modal = document.createElement('div');
            const modalId = `modal-${Date.now()}`;
            modal.id = modalId;
            
            // Button colors based on type
            const buttonColors = {
                primary: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
                danger: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
                success: 'bg-green-600 hover:bg-green-700 focus:ring-green-500',
                warning: 'bg-yellow-500 hover:bg-yellow-600 focus:ring-yellow-500'
            };
            
            // Default icons for types
            const typeIcons = {
                primary: `<svg class="h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>`,
                danger: `<svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>`,
                success: `<svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                           </svg>`,
                warning: `<svg class="h-6 w-6 text-yellow-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                           </svg>`
            };
            
            // Create modal content
            modal.innerHTML = `
                <div class="fixed z-50 inset-0 overflow-y-auto">
                    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" aria-hidden="true"></div>
                        
                        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        
                        <div class="glass dark:glass-dark inline-block align-bottom rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div class="sm:flex sm:items-start">
                                    ${icon || typeIcons[type] ? `
                                        <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-${type}-100 sm:mx-0 sm:h-10 sm:w-10">
                                            ${icon || typeIcons[type]}
                                        </div>
                                    ` : ''}
                                    
                                    <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                                        <h3 class="text-lg leading-6 font-medium">${title}</h3>
                                        <div class="mt-2">
                                            <p class="text-sm text-gray-500 dark:text-gray-400">${message}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                <button type="button" class="modal-confirm w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white ${buttonColors[type] || buttonColors.primary} focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm">
                                    ${confirmText}
                                </button>
                                <button type="button" class="modal-cancel mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white dark:bg-gray-700 text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                                    ${cancelText}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal to container
            container.appendChild(modal);
            
            // Close function
            const close = (result) => {
                modal.classList.add('opacity-0');
                
                // Remove after animation
                setTimeout(() => {
                    modal.remove();
                    resolve(result);
                    
                    // Remove container if empty
                    if (container.children.length === 0) {
                        container.remove();
                    }
                }, 200);
            };
            
            // Confirm button click handler
            modal.querySelector('.modal-confirm').addEventListener('click', () => close(true));
            
            // Cancel button click handler
            modal.querySelector('.modal-cancel').addEventListener('click', () => close(false));
            
            // Close on backdrop click if allowed
            if (options.closeOnBackdropClick !== false) {
                modal.querySelector('.fixed.inset-0').addEventListener('click', (event) => {
                    if (event.target === event.currentTarget) {
                        close(false);
                    }
                });
            }
            
            // Close on escape key if allowed
            if (options.closeOnEscape !== false) {
                const escHandler = (event) => {
                    if (event.key === 'Escape') {
                        close(false);
                        document.removeEventListener('keydown', escHandler);
                    }
                };
                
                document.addEventListener('keydown', escHandler);
            }
        });
    }
    
    /**
     * Show a custom modal
     * @param {Object} options - Modal options
     * @returns {Object} Modal control object
     */
    static custom(options) {
        const {
            content = '',
            width = 'max-w-lg',
            closeOnBackdropClick = true,
            closeOnEscape = true,
            onClose = null
        } = options;
        
        // Create modal container if it doesn't exist
        let container = document.getElementById('modal-container');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'modal-container';
            document.body.appendChild(container);
        }
        
        // Create modal element
        const modal = document.createElement('div');
        const modalId = `modal-${Date.now()}`;
        modal.id = modalId;
        
        // Create modal content
        modal.innerHTML = `
            <div class="fixed z-50 inset-0 overflow-y-auto">
                <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity modal-backdrop" aria-hidden="true"></div>
                    
                    <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                    
                    <div class="glass dark:glass-dark inline-block align-bottom rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle ${width} sm:w-full">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to container
        container.appendChild(modal);
        
        // Close function
        const close = () => {
            modal.classList.add('opacity-0');
            
            // Remove after animation
            setTimeout(() => {
                modal.remove();
                
                // Call close callback if provided
                if (onClose) {
                    onClose();
                }
                
                // Remove container if empty
                if (container.children.length === 0) {
                    container.remove();
                }
            }, 200);
        };
        
        // Close on backdrop click if allowed
        if (closeOnBackdropClick) {
            modal.querySelector('.modal-backdrop').addEventListener('click', (event) => {
                if (event.target === event.currentTarget) {
                    close();
                }
            });
        }
        
        // Close on escape key if allowed
        if (closeOnEscape) {
            const escHandler = (event) => {
                if (event.key === 'Escape') {
                    close();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            
            document.addEventListener('keydown', escHandler);
        }
        
        // Return an object to control the modal
        return {
            id: modalId,
            close,
            
            /**
             * Update the modal content
             * @param {string} newContent - New content
             */
            setContent(newContent) {
                const contentEl = modal.querySelector('.glass');
                if (contentEl) {
                    contentEl.innerHTML = newContent;
                }
            }
        };
    }
}

// Register the components globally
window.Button = Button;
window.Card = Card;
window.Alert = Alert;
window.Badge = Badge;
window.Avatar = Avatar;
window.Dropdown = Dropdown;
window.Toast = Toast;
window.Modal = Modal;