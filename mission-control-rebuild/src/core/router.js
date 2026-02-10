/**
 * Router for the Mission Control Dashboard
 * Handles client-side routing for the single-page application
 */

const Router = (function() {
    // Private properties
    const _routes = [];
    let _notFoundHandler = null;
    let _currentRoute = null;
    
    // Default container
    let _container = null;
    
    /**
     * Route change handler
     * @param {string} path - The new path
     * @param {Object} params - Route parameters
     * @private
     */
    const _handleRouteChange = (path, params = {}) => {
        // Find the matching route
        const route = _routes.find(route => {
            if (typeof route.path === 'string') {
                return route.path === path;
            } else if (route.path instanceof RegExp) {
                return route.path.test(path);
            }
            return false;
        });
        
        // Call not found handler if no route matches
        if (!route && _notFoundHandler) {
            _currentRoute = null;
            _notFoundHandler(path);
            return;
        }
        
        if (!route) {
            console.warn(`No route found for path: ${path}`);
            return;
        }
        
        // Extract route parameters if path is a regex
        if (route.path instanceof RegExp) {
            const match = path.match(route.path);
            if (match && match.groups) {
                params = { ...params, ...match.groups };
            }
        }
        
        // Update current route
        _currentRoute = {
            path,
            params,
            route
        };
        
        // Notify state management about the route change
        State.set('app.currentView', route.name);
        
        // Call the route handler
        route.handler(params);
        
        // Emit route change event
        EventBus.emit(Events.ROUTE_CHANGE, {
            path,
            route: route.name,
            params
        });
    };
    
    /**
     * Parse the current URL and extract the path
     * @returns {string} The current path
     * @private
     */
    const _getPathFromUrl = () => {
        // Get path from hash (for hash-based routing)
        const hash = window.location.hash.slice(1);
        
        if (hash) {
            // Extract path and query parameters
            const [path, queryString] = hash.split('?');
            return path;
        }
        
        return '/';
    };
    
    /**
     * Parse query parameters from the URL
     * @returns {Object} Query parameters object
     * @private
     */
    const _getQueryParams = () => {
        const params = {};
        
        // Get query string from hash (for hash-based routing)
        const hash = window.location.hash.slice(1);
        const queryString = hash.split('?')[1];
        
        if (queryString) {
            const searchParams = new URLSearchParams(queryString);
            for (const [key, value] of searchParams.entries()) {
                params[key] = value;
            }
        }
        
        return params;
    };
    
    /**
     * Render a template in the container
     * @param {string} template - HTML template
     * @private
     */
    const _renderTemplate = (template) => {
        if (_container) {
            _container.innerHTML = template;
        }
    };
    
    return {
        /**
         * Initialize the router
         * @param {HTMLElement} container - Container element for rendering views
         * @param {Object} options - Router options
         */
        init(container, options = {}) {
            _container = container;
            
            // Setup event listener for hash changes (for hash-based routing)
            window.addEventListener('hashchange', () => {
                const path = _getPathFromUrl();
                const params = _getQueryParams();
                _handleRouteChange(path, params);
            });
            
            // Navigate to the current URL on initialization
            if (options.triggerInitialRoute !== false) {
                setTimeout(() => {
                    const path = _getPathFromUrl();
                    const params = _getQueryParams();
                    _handleRouteChange(path, params);
                }, 0);
            }
        },
        
        /**
         * Add a route
         * @param {string|RegExp} path - Route path or regex pattern
         * @param {Function} handler - Route handler
         * @param {string} name - Route name
         */
        add(path, handler, name) {
            _routes.push({ path, handler, name });
        },
        
        /**
         * Set the not found handler
         * @param {Function} handler - Not found handler
         */
        setNotFound(handler) {
            _notFoundHandler = handler;
        },
        
        /**
         * Navigate to a route
         * @param {string} path - Path to navigate to
         * @param {Object} params - Query parameters
         * @param {Object} options - Navigation options
         */
        navigate(path, params = {}, options = {}) {
            // Build query string
            let queryString = '';
            
            if (Object.keys(params).length > 0) {
                const searchParams = new URLSearchParams();
                for (const [key, value] of Object.entries(params)) {
                    searchParams.append(key, value);
                }
                queryString = `?${searchParams.toString()}`;
            }
            
            // Update the URL
            if (options.replace) {
                window.location.replace(`#${path}${queryString}`);
            } else {
                window.location.hash = `${path}${queryString}`;
            }
        },
        
        /**
         * Get the current route
         * @returns {Object|null} Current route or null
         */
        getCurrentRoute() {
            return _currentRoute;
        },
        
        /**
         * Check if a path matches the current route
         * @param {string} path - Path to check
         * @returns {boolean} Whether the path matches
         */
        isActive(path) {
            if (!_currentRoute) {
                return false;
            }
            
            return _currentRoute.path === path;
        },
        
        /**
         * Get the container element
         * @returns {HTMLElement} Container element
         */
        getContainer() {
            return _container;
        },
        
        /**
         * Render a component in a specific container
         * @param {string} container - Container selector
         * @param {string} componentClass - Component class name
         * @param {Object} options - Component options
         * @returns {Component} The component instance
         */
        renderComponent(container, componentClass, options = {}) {
            const containerEl = document.querySelector(container);
            
            if (!containerEl) {
                console.warn(`Container not found: ${container}`);
                return null;
            }
            
            // Clear the container
            containerEl.innerHTML = '';
            
            // Create the component instance
            const ComponentClass = window[componentClass] || Component;
            return new ComponentClass(containerEl, options);
        },
        
        /**
         * Render a template in the main container
         * @param {string} template - HTML template
         */
        renderTemplate(template) {
            _renderTemplate(template);
        }
    };
})();