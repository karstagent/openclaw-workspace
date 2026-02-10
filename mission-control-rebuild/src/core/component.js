/**
 * Component System for Mission Control Dashboard
 * Provides a base class for creating reusable UI components
 */

class Component {
    /**
     * Create a new component
     * @param {HTMLElement|string} el - DOM element or selector for the component container
     * @param {Object} options - Component options
     */
    constructor(el, options = {}) {
        // Store options
        this.options = options;
        
        // Store template if provided
        this.template = options.template || '';
        
        // Initialize state subscriptions
        this.subscriptions = [];
        
        // Find the element in the DOM if a selector was provided
        if (typeof el === 'string') {
            this.el = document.querySelector(el);
            
            if (!this.el) {
                console.warn(`Element not found: ${el}`);
                return;
            }
        } else {
            this.el = el;
        }
        
        // Add a data attribute to identify this component in the DOM
        this.componentId = Helpers.generateId();
        this.el.dataset.componentId = this.componentId;
        
        // Set up class name if provided
        if (options.className) {
            this.el.classList.add(options.className);
        }
        
        // Initialize component
        this.init();
        
        // Render the component
        this.render();
        
        // Set up event listeners
        this.setupEvents();
    }
    
    /**
     * Initialize the component (to be overridden by subclasses)
     */
    init() {}
    
    /**
     * Render the component content (to be overridden by subclasses)
     */
    render() {
        // Only use the template if it exists and no custom render is provided
        if (this.template) {
            this.el.innerHTML = this.template;
        }
    }
    
    /**
     * Set up event listeners (to be overridden by subclasses)
     */
    setupEvents() {}
    
    /**
     * Update the component with new data
     * @param {Object} data - New data
     */
    update(data) {
        this.options.data = { ...this.options.data, ...data };
        this.render();
    }
    
    /**
     * Subscribe to state changes
     * @param {string} path - State path to subscribe to
     * @param {Function} callback - Function to call when state changes
     */
    subscribe(path, callback) {
        const unsubscribe = State.subscribe(path, callback);
        this.subscriptions.push(unsubscribe);
        return unsubscribe;
    }
    
    /**
     * Find an element within the component
     * @param {string} selector - CSS selector
     * @returns {HTMLElement|null} - The found element or null
     */
    find(selector) {
        return this.el.querySelector(selector);
    }
    
    /**
     * Find all elements matching a selector within the component
     * @param {string} selector - CSS selector
     * @returns {NodeList} - The found elements
     */
    findAll(selector) {
        return this.el.querySelectorAll(selector);
    }
    
    /**
     * Add an event listener to an element within the component
     * @param {string|HTMLElement} selector - CSS selector or element
     * @param {string} event - Event name
     * @param {Function} callback - Event handler
     */
    on(selector, event, callback) {
        let elements;
        
        if (typeof selector === 'string') {
            elements = this.findAll(selector);
            
            if (elements.length === 0) {
                console.warn(`No elements found for selector: ${selector}`);
                return;
            }
        } else {
            elements = [selector];
        }
        
        elements.forEach(element => {
            element.addEventListener(event, callback.bind(this));
        });
    }
    
    /**
     * Remove the component from the DOM and clean up
     */
    remove() {
        // Remove event listeners
        this.cleanup();
        
        // Remove the element from the DOM
        this.el.remove();
    }
    
    /**
     * Clean up resources used by the component
     */
    cleanup() {
        // Unsubscribe from all state subscriptions
        this.subscriptions.forEach(unsubscribe => unsubscribe());
        this.subscriptions = [];
    }
    
    /**
     * Create a new component and append it to the current component
     * @param {string} componentClass - Component class name
     * @param {Object} options - Component options
     * @param {string} [targetSelector] - Selector for the target container (defaults to this.el)
     * @returns {Component} The new component instance
     */
    createChild(componentClass, options, targetSelector) {
        const targetEl = targetSelector ? this.find(targetSelector) : this.el;
        
        if (!targetEl) {
            console.warn(`Target element not found: ${targetSelector}`);
            return null;
        }
        
        // Create a new element for the component
        const el = document.createElement('div');
        targetEl.appendChild(el);
        
        // Create the component instance
        const ComponentClass = window[componentClass] || Component;
        return new ComponentClass(el, options);
    }
}

// Common component factory for convenient component creation
function createComponent(selector, options = {}) {
    const elements = document.querySelectorAll(selector);
    const components = [];
    
    elements.forEach(el => {
        const componentClass = options.component || Component;
        const ComponentClass = window[componentClass] || Component;
        components.push(new ComponentClass(el, options));
    });
    
    return components.length === 1 ? components[0] : components;
}

// Specialized component classes

/**
 * List Component - For rendering lists of items
 */
class ListComponent extends Component {
    /**
     * Initialize the list component
     */
    init() {
        super.init();
        
        this.items = this.options.items || [];
        this.itemTemplate = this.options.itemTemplate || '';
        this.itemComponent = this.options.itemComponent;
        this.emptyMessage = this.options.emptyMessage || 'No items to display';
        this.itemsContainer = this.options.itemsContainer || this.el;
        this.itemsContainerSelector = this.options.itemsContainerSelector || null;
    }
    
    /**
     * Render the list
     */
    render() {
        if (this.template) {
            this.el.innerHTML = this.template;
            
            if (this.itemsContainerSelector) {
                this.itemsContainer = this.find(this.itemsContainerSelector);
            }
        }
        
        // Clear previous items
        if (this.itemsContainer !== this.el) {
            this.itemsContainer.innerHTML = '';
        }
        
        // Show empty message if no items
        if (this.items.length === 0) {
            if (this.itemsContainer === this.el) {
                this.el.innerHTML = `<div class="empty-message">${this.emptyMessage}</div>`;
            } else {
                this.itemsContainer.innerHTML = `<div class="empty-message">${this.emptyMessage}</div>`;
            }
            return;
        }
        
        // Render items
        this.renderItems();
    }
    
    /**
     * Render the list items
     */
    renderItems() {
        this.itemsContainer.innerHTML = '';
        
        this.items.forEach((item, index) => {
            if (this.itemComponent) {
                // Create child component for each item
                const itemEl = document.createElement('div');
                this.itemsContainer.appendChild(itemEl);
                
                const ComponentClass = window[this.itemComponent] || Component;
                new ComponentClass(itemEl, {
                    data: item,
                    index,
                    parent: this
                });
            } else {
                // Use template for each item
                const itemEl = document.createElement('div');
                itemEl.innerHTML = this.renderItemTemplate(item, index);
                
                // Move the child elements to the container (not the wrapper div)
                while (itemEl.firstChild) {
                    this.itemsContainer.appendChild(itemEl.firstChild);
                }
            }
        });
    }
    
    /**
     * Render a single item using the template
     * @param {Object} item - The item data
     * @param {number} index - Item index
     * @returns {string} - The rendered HTML
     */
    renderItemTemplate(item, index) {
        if (!this.itemTemplate) {
            return `<div>${JSON.stringify(item)}</div>`;
        }
        
        return this.itemTemplate.replace(/{{\s*(.+?)\s*}}/g, (_, key) => {
            const keys = key.split('.');
            let value = item;
            
            for (const k of keys) {
                if (value === undefined || value === null) {
                    return '';
                }
                value = value[k];
            }
            
            return Helpers.escapeHtml(value !== undefined ? value.toString() : '');
        });
    }
    
    /**
     * Update the list items
     * @param {Array} items - New items
     */
    updateItems(items) {
        this.items = items || [];
        this.render();
    }
}

/**
 * Form Component - For handling forms
 */
class FormComponent extends Component {
    /**
     * Initialize the form component
     */
    init() {
        super.init();
        
        this.formData = this.options.data || {};
        this.submitHandler = this.options.onSubmit;
        this.resetHandler = this.options.onReset;
    }
    
    /**
     * Set up form events
     */
    setupEvents() {
        // Form submission
        this.on(this.el, 'submit', (event) => {
            event.preventDefault();
            
            const formData = new FormData(this.el);
            const data = {};
            
            for (const [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            if (this.submitHandler) {
                this.submitHandler(data, this);
            }
        });
        
        // Form reset
        this.on(this.el, 'reset', (event) => {
            if (this.resetHandler) {
                this.resetHandler(this);
            }
        });
        
        // Input changes for realtime validation
        this.findAll('input, select, textarea').forEach(input => {
            input.addEventListener('change', () => {
                this.validateField(input);
            });
            
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }
    
    /**
     * Validate a form field
     * @param {HTMLElement} field - The field to validate
     * @returns {boolean} - Whether the field is valid
     */
    validateField(field) {
        // Clear previous validation messages
        const container = field.parentElement;
        const errorEl = container.querySelector('.error-message');
        
        if (errorEl) {
            errorEl.remove();
        }
        
        // Check validity
        if (!field.checkValidity()) {
            // Create error message
            const message = document.createElement('div');
            message.className = 'error-message text-red-500 text-sm mt-1';
            message.innerText = field.validationMessage;
            
            container.appendChild(message);
            return false;
        }
        
        return true;
    }
    
    /**
     * Validate the entire form
     * @returns {boolean} - Whether the form is valid
     */
    validate() {
        let isValid = true;
        
        this.findAll('input, select, textarea').forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Set form data
     * @param {Object} data - Form data
     */
    setData(data) {
        this.formData = data;
        
        // Set input values
        for (const [key, value] of Object.entries(data)) {
            const field = this.find(`[name="${key}"]`);
            
            if (field) {
                // Handle different field types
                if (field.type === 'checkbox') {
                    field.checked = !!value;
                } else if (field.type === 'radio') {
                    const radio = this.find(`[name="${key}"][value="${value}"]`);
                    if (radio) {
                        radio.checked = true;
                    }
                } else {
                    field.value = value;
                }
            }
        }
    }
    
    /**
     * Get form data
     * @returns {Object} - The form data
     */
    getData() {
        const formData = new FormData(this.el);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    /**
     * Reset the form
     */
    reset() {
        this.el.reset();
        
        // Clear validation messages
        this.findAll('.error-message').forEach(el => el.remove());
    }
}

/**
 * Modal Component - For displaying modal dialogs
 */
class ModalComponent extends Component {
    /**
     * Initialize the modal
     */
    init() {
        super.init();
        
        this.isOpen = false;
        this.closeOnEscape = this.options.closeOnEscape !== false;
        this.closeOnOutsideClick = this.options.closeOnOutsideClick !== false;
    }
    
    /**
     * Set up modal events
     */
    setupEvents() {
        // Close button
        this.on('.modal-close', 'click', this.close);
        
        // Close on outside click
        if (this.closeOnOutsideClick) {
            this.el.addEventListener('click', (event) => {
                if (event.target === this.el) {
                    this.close();
                }
            });
        }
        
        // Close on escape key
        if (this.closeOnEscape) {
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }
    }
    
    /**
     * Open the modal
     * @param {Object} data - Optional data to pass to the modal
     */
    open(data) {
        if (data) {
            this.update(data);
        }
        
        this.isOpen = true;
        this.el.classList.remove('hidden');
        
        // Add animation classes
        this.el.classList.add('fade-in');
        
        // Focus the first focusable element
        setTimeout(() => {
            const focusable = this.el.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (focusable) {
                focusable.focus();
            }
        }, 50);
        
        // Trigger open event
        EventBus.emit(Events.MODAL_OPEN, { id: this.componentId });
    }
    
    /**
     * Close the modal
     */
    close() {
        this.isOpen = false;
        
        // Add animation class for fade out
        this.el.classList.add('fade-out');
        
        // Remove the modal after animation completes
        setTimeout(() => {
            this.el.classList.remove('fade-in', 'fade-out');
            this.el.classList.add('hidden');
            
            // Trigger close event
            EventBus.emit(Events.MODAL_CLOSE, { id: this.componentId });
        }, 300);
    }
}

/**
 * Tab Component - For tabbed interfaces
 */
class TabComponent extends Component {
    /**
     * Initialize the tab component
     */
    init() {
        super.init();
        
        this.tabs = this.options.tabs || [];
        this.activeTab = this.options.activeTab || 0;
    }
    
    /**
     * Render tabs
     */
    render() {
        // Create tab navigation
        let tabNavHtml = '<div class="tab-nav flex border-b border-gray-200 dark:border-gray-700">';
        
        this.tabs.forEach((tab, index) => {
            const isActive = index === this.activeTab;
            tabNavHtml += `
                <button class="tab-button py-2 px-4 font-medium ${isActive ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-blue-500'}" 
                        data-tab-index="${index}">
                    ${tab.label}
                </button>
            `;
        });
        
        tabNavHtml += '</div>';
        
        // Create tab content
        let tabContentHtml = '<div class="tab-content pt-4">';
        
        this.tabs.forEach((tab, index) => {
            const isActive = index === this.activeTab;
            tabContentHtml += `
                <div class="tab-panel ${isActive ? '' : 'hidden'}" data-tab-index="${index}">
                    ${tab.content}
                </div>
            `;
        });
        
        tabContentHtml += '</div>';
        
        this.el.innerHTML = tabNavHtml + tabContentHtml;
    }
    
    /**
     * Set up tab events
     */
    setupEvents() {
        this.on('.tab-button', 'click', (event) => {
            const tabIndex = parseInt(event.currentTarget.dataset.tabIndex, 10);
            this.activateTab(tabIndex);
        });
    }
    
    /**
     * Activate a tab
     * @param {number} tabIndex - Index of the tab to activate
     */
    activateTab(tabIndex) {
        // Make sure the tab index is valid
        if (tabIndex < 0 || tabIndex >= this.tabs.length) {
            return;
        }
        
        // Deactivate all tabs
        this.findAll('.tab-button').forEach(button => {
            button.classList.remove('border-b-2', 'border-blue-500', 'text-blue-500');
            button.classList.add('text-gray-500', 'hover:text-blue-500');
        });
        
        this.findAll('.tab-panel').forEach(panel => {
            panel.classList.add('hidden');
        });
        
        // Activate the selected tab
        const activeButton = this.find(`.tab-button[data-tab-index="${tabIndex}"]`);
        if (activeButton) {
            activeButton.classList.remove('text-gray-500', 'hover:text-blue-500');
            activeButton.classList.add('border-b-2', 'border-blue-500', 'text-blue-500');
        }
        
        const activePanel = this.find(`.tab-panel[data-tab-index="${tabIndex}"]`);
        if (activePanel) {
            activePanel.classList.remove('hidden');
        }
        
        // Update the active tab
        this.activeTab = tabIndex;
    }
}