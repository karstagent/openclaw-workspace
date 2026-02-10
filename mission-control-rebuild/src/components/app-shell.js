/**
 * App Shell Component
 * Main application container that manages the overall layout and structure
 */

class AppShell extends Component {
    init() {
        super.init();
        
        // Initialize properties
        this.sidebarOpen = State.get('app.sidebarOpen') || true;
        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.currentView = State.get('app.currentView') || 'dashboard';
        
        // Subscribe to state changes
        this.subscribe('app.sidebarOpen', (value) => {
            this.sidebarOpen = value;
            this.updateSidebar();
        });
        
        this.subscribe('app.currentView', (value) => {
            this.currentView = value;
            this.updateNavigation();
        });
    }
    
    render() {
        this.el.innerHTML = `
            <div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
                <!-- Top Navigation Bar -->
                <nav class="glass dark:glass-dark border-b border-gray-200 dark:border-gray-700 fixed w-full top-0 z-30">
                    <div class="px-4 sm:px-6 lg:px-8">
                        <div class="flex justify-between h-16">
                            <!-- Left side -->
                            <div class="flex">
                                <!-- Mobile sidebar button -->
                                <div class="flex items-center mr-2 -ml-2 md:hidden">
                                    <button id="mobile-sidebar-toggle" class="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none">
                                        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                                        </svg>
                                    </button>
                                </div>
                                
                                <!-- Logo and app name -->
                                <div class="flex items-center">
                                    <img class="h-8 w-auto" src="https://ui-avatars.com/api/?name=MC&color=fff&background=3b82f6&bold=true&font-size=0.5" alt="Mission Control">
                                    <span class="ml-2 text-lg font-semibold">Mission Control</span>
                                </div>
                                
                                <!-- Desktop navigation -->
                                <div class="hidden md:ml-6 md:flex md:items-center">
                                    <div class="ml-4 flex items-center md:ml-6">
                                        <!-- Main navigation buttons -->
                                        <a href="#/" class="nav-link px-3 py-2 rounded-md text-sm font-medium ${this.currentView === 'dashboard' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'}" data-view="dashboard">Dashboard</a>
                                        <a href="#/tasks" class="nav-link px-3 py-2 rounded-md text-sm font-medium ${this.currentView === 'tasks' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'}" data-view="tasks">Tasks</a>
                                        <a href="#/projects" class="nav-link px-3 py-2 rounded-md text-sm font-medium ${this.currentView === 'projects' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'}" data-view="projects">Projects</a>
                                        <a href="#/calendar" class="nav-link px-3 py-2 rounded-md text-sm font-medium ${this.currentView === 'calendar' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'}" data-view="calendar">Calendar</a>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Right side -->
                            <div class="flex items-center">
                                <!-- Search -->
                                <div class="relative mx-2">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    </div>
                                    <input type="text" id="search-input" class="glass dark:glass-dark w-48 sm:w-64 md:w-72 pl-10 pr-3 py-2 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Search tasks, projects...">
                                </div>
                                
                                <!-- Quick Actions Button -->
                                <button id="quick-actions-btn" class="p-1 ml-3 rounded-full text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                    </svg>
                                </button>
                                
                                <!-- Quick Actions Dropdown -->
                                <div id="quick-actions-dropdown" class="hidden absolute right-24 top-16 z-10 mt-2 glass dark:glass-dark rounded-md shadow-lg p-1">
                                    <a href="#" id="new-task-btn" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">New Task</a>
                                    <a href="#" id="new-project-btn" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">New Project</a>
                                    <a href="#" id="export-data-btn" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">Export Data</a>
                                </div>
                                
                                <!-- Dark Mode Toggle -->
                                <button id="theme-toggle" class="p-1 ml-3 rounded-full text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <!-- Sun icon (light mode) -->
                                    <svg id="theme-toggle-light-icon" class="${this.darkMode ? 'hidden' : ''} h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                                    </svg>
                                    <!-- Moon icon (dark mode) -->
                                    <svg id="theme-toggle-dark-icon" class="${this.darkMode ? '' : 'hidden'} h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                    </svg>
                                </button>
                                
                                <!-- Notifications -->
                                <button id="notifications-btn" class="p-1 ml-3 rounded-full relative text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                    </svg>
                                    <span id="notifications-counter" class="hidden absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500"></span>
                                </button>
                                
                                <!-- Notifications Dropdown -->
                                <div id="notifications-dropdown" class="hidden absolute right-12 top-16 z-10 mt-2 glass dark:glass-dark rounded-md shadow-lg p-1 w-80">
                                    <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                                        <h3 class="text-sm font-medium">Notifications</h3>
                                    </div>
                                    <div id="notifications-list" class="max-h-64 overflow-y-auto p-2">
                                        <p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No new notifications</p>
                                    </div>
                                    <div class="px-4 py-2 border-t border-gray-200 dark:border-gray-700 text-center">
                                        <a href="#/notifications" class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">View all</a>
                                    </div>
                                </div>
                                
                                <!-- Profile Dropdown -->
                                <div class="ml-3 relative">
                                    <div>
                                        <button id="user-menu-button" class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" aria-expanded="false" aria-haspopup="true">
                                            <img class="h-8 w-8 rounded-full" src="https://ui-avatars.com/api/?name=Jordan&background=random" alt="User Avatar">
                                        </button>
                                    </div>
                                    <div id="user-menu" class="hidden absolute right-0 z-10 mt-2 glass dark:glass-dark rounded-md shadow-lg p-1 w-48" role="menu" aria-orientation="vertical" aria-labelledby="user-menu-button">
                                        <a href="#/profile" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md" role="menuitem">Your Profile</a>
                                        <a href="#/settings" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md" role="menuitem">Settings</a>
                                        <a href="#/help" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md" role="menuitem">Help</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Mobile Navigation Menu -->
                    <div id="mobile-nav-menu" class="hidden md:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                        <div class="px-2 pt-2 pb-3 space-y-1">
                            <a href="#/" class="nav-link block px-3 py-2 rounded-md text-base font-medium ${this.currentView === 'dashboard' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="dashboard">Dashboard</a>
                            <a href="#/tasks" class="nav-link block px-3 py-2 rounded-md text-base font-medium ${this.currentView === 'tasks' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="tasks">Tasks</a>
                            <a href="#/projects" class="nav-link block px-3 py-2 rounded-md text-base font-medium ${this.currentView === 'projects' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="projects">Projects</a>
                            <a href="#/calendar" class="nav-link block px-3 py-2 rounded-md text-base font-medium ${this.currentView === 'calendar' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="calendar">Calendar</a>
                        </div>
                    </div>
                </nav>
                
                <!-- Page Container -->
                <div class="flex h-screen pt-16">
                    <!-- Sidebar -->
                    <div id="sidebar" class="glass dark:glass-dark hidden md:flex md:flex-shrink-0 border-r border-gray-200 dark:border-gray-700 ${this.sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300">
                        <div class="flex flex-col w-full">
                            <!-- Sidebar toggle button -->
                            <div class="flex justify-end p-4">
                                <button id="sidebar-toggle" class="p-1 rounded-full text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none">
                                    <svg class="h-5 w-5 transform ${this.sidebarOpen ? 'rotate-180' : ''}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                                    </svg>
                                </button>
                            </div>
                            
                            <!-- Navigation -->
                            <nav class="mt-2 flex-1 px-4 space-y-1">
                                <!-- Dashboard -->
                                <a href="#/" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'dashboard' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="dashboard">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'dashboard' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Dashboard</span>
                                </a>
                                
                                <!-- Tasks -->
                                <a href="#/tasks" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'tasks' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="tasks">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'tasks' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Tasks</span>
                                </a>
                                
                                <!-- Projects -->
                                <a href="#/projects" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'projects' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="projects">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'projects' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Projects</span>
                                </a>
                                
                                <!-- Calendar -->
                                <a href="#/calendar" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'calendar' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="calendar">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'calendar' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Calendar</span>
                                </a>
                                
                                <!-- Team -->
                                <a href="#/team" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'team' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="team">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'team' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Team</span>
                                </a>
                                
                                <!-- Reports -->
                                <a href="#/reports" class="sidebar-nav-link group flex items-center px-2 py-2 text-sm font-medium rounded-md ${this.currentView === 'reports' ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900' : 'text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'}" data-view="reports">
                                    <svg class="mr-3 h-5 w-5 ${this.currentView === 'reports' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                    <span class="${this.sidebarOpen ? '' : 'hidden'}">Reports</span>
                                </a>
                            </nav>
                            
                            <!-- Projects List (when sidebar is open) -->
                            <div class="mt-8 px-4 ${this.sidebarOpen ? '' : 'hidden'}">
                                <h3 class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Projects</h3>
                                <div id="sidebar-projects-list" class="mt-1 space-y-1">
                                    <!-- Projects will be loaded here -->
                                    <div class="text-center py-4">
                                        <div class="w-5 h-5 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <a href="#/projects/new" class="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700">
                                        <svg class="mr-3 h-5 w-5 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                        </svg>
                                        New Project
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Main Content Area -->
                    <div class="flex-1 relative z-0 overflow-auto focus:outline-none">
                        <main class="p-4">
                            <div id="content-container" class="max-w-7xl mx-auto">
                                <!-- Page content will be loaded here -->
                                <div class="flex items-center justify-center h-full">
                                    <div class="text-center">
                                        <div class="w-12 h-12 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto mb-4"></div>
                                        <h2 class="text-xl font-semibold">Loading...</h2>
                                        <p class="text-gray-500 dark:text-gray-400 mt-2">Please wait while we load your content</p>
                                    </div>
                                </div>
                            </div>
                        </main>
                    </div>
                </div>
                
                <!-- New Task Modal -->
                <div id="new-task-modal" class="hidden fixed z-50 inset-0 overflow-y-auto">
                    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
                        
                        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
                        
                        <div id="new-task-modal-content" class="glass dark:glass-dark inline-block align-bottom rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <!-- Modal content will be loaded here -->
                            <div class="p-6">
                                <div class="w-5 h-5 border-t-2 border-blue-500 border-r-2 border-b-2 rounded-full animate-spin mx-auto"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Toast Container -->
                <div id="toast-container" class="fixed bottom-4 right-4 z-50"></div>
            </div>
        `;
    }
    
    setupEvents() {
        // Sidebar toggle button
        this.on('#sidebar-toggle', 'click', () => {
            const newValue = !this.sidebarOpen;
            State.set('app.sidebarOpen', newValue);
        });
        
        // Mobile sidebar toggle
        this.on('#mobile-sidebar-toggle', 'click', () => {
            const mobileMenu = this.find('#mobile-nav-menu');
            mobileMenu.classList.toggle('hidden');
        });
        
        // Theme toggle
        this.on('#theme-toggle', 'click', () => {
            this.darkMode = !this.darkMode;
            this.toggleDarkMode();
        });
        
        // User menu toggle
        this.on('#user-menu-button', 'click', () => {
            const userMenu = this.find('#user-menu');
            userMenu.classList.toggle('hidden');
        });
        
        // Quick actions toggle
        this.on('#quick-actions-btn', 'click', () => {
            const actionsMenu = this.find('#quick-actions-dropdown');
            actionsMenu.classList.toggle('hidden');
        });
        
        // Notifications toggle
        this.on('#notifications-btn', 'click', () => {
            const notificationsMenu = this.find('#notifications-dropdown');
            notificationsMenu.classList.toggle('hidden');
        });
        
        // New task button
        this.on('#new-task-btn', 'click', (e) => {
            e.preventDefault();
            this.openNewTaskModal();
            this.find('#quick-actions-dropdown').classList.add('hidden');
        });
        
        // New project button
        this.on('#new-project-btn', 'click', (e) => {
            e.preventDefault();
            this.openNewProjectModal();
            this.find('#quick-actions-dropdown').classList.add('hidden');
        });
        
        // Export data button
        this.on('#export-data-btn', 'click', (e) => {
            e.preventDefault();
            this.exportData();
            this.find('#quick-actions-dropdown').classList.add('hidden');
        });
        
        // Search input
        this.on('#search-input', 'input', Helpers.debounce((e) => {
            const query = e.target.value.trim();
            State.set('tasks.filters.search', query);
        }, 300));
        
        // Navigation links
        this.on('.nav-link', 'click', (e) => {
            const view = e.currentTarget.dataset.view;
            if (view) {
                State.set('app.currentView', view);
            }
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#user-menu-button') && !e.target.closest('#user-menu')) {
                this.find('#user-menu').classList.add('hidden');
            }
            
            if (!e.target.closest('#quick-actions-btn') && !e.target.closest('#quick-actions-dropdown')) {
                this.find('#quick-actions-dropdown').classList.add('hidden');
            }
            
            if (!e.target.closest('#notifications-btn') && !e.target.closest('#notifications-dropdown')) {
                this.find('#notifications-dropdown').classList.add('hidden');
            }
        });
        
        // Load projects for sidebar
        this.loadProjects();
        
        // Initialize based on system preference
        this.initDarkMode();
    }
    
    /**
     * Update the sidebar when the state changes
     */
    updateSidebar() {
        const sidebar = this.find('#sidebar');
        const sidebarToggleIcon = this.find('#sidebar-toggle svg');
        const sidebarLabels = this.findAll('#sidebar span');
        const projectsList = this.find('#sidebar-projects-list').parentElement;
        
        if (this.sidebarOpen) {
            sidebar.classList.remove('w-16');
            sidebar.classList.add('w-64');
            sidebarToggleIcon.classList.add('rotate-180');
            
            sidebarLabels.forEach(label => {
                label.classList.remove('hidden');
            });
            
            projectsList.classList.remove('hidden');
        } else {
            sidebar.classList.remove('w-64');
            sidebar.classList.add('w-16');
            sidebarToggleIcon.classList.remove('rotate-180');
            
            sidebarLabels.forEach(label => {
                label.classList.add('hidden');
            });
            
            projectsList.classList.add('hidden');
        }
    }
    
    /**
     * Update the navigation when the current view changes
     */
    updateNavigation() {
        // Update main navigation links
        const navLinks = this.findAll('.nav-link');
        navLinks.forEach(link => {
            const view = link.dataset.view;
            
            if (view === this.currentView) {
                if (link.classList.contains('block')) {
                    // Mobile nav
                    link.classList.add('text-blue-600', 'dark:text-blue-400', 'bg-blue-50', 'dark:bg-blue-900');
                    link.classList.remove('text-gray-600', 'dark:text-gray-200', 'hover:bg-gray-50', 'dark:hover:bg-gray-700');
                } else {
                    // Desktop nav
                    link.classList.add('text-blue-600', 'dark:text-blue-400');
                    link.classList.remove('text-gray-500', 'dark:text-gray-400', 'hover:text-gray-900', 'dark:hover:text-gray-200');
                }
            } else {
                if (link.classList.contains('block')) {
                    // Mobile nav
                    link.classList.remove('text-blue-600', 'dark:text-blue-400', 'bg-blue-50', 'dark:bg-blue-900');
                    link.classList.add('text-gray-600', 'dark:text-gray-200', 'hover:bg-gray-50', 'dark:hover:bg-gray-700');
                } else {
                    // Desktop nav
                    link.classList.remove('text-blue-600', 'dark:text-blue-400');
                    link.classList.add('text-gray-500', 'dark:text-gray-400', 'hover:text-gray-900', 'dark:hover:text-gray-200');
                }
            }
        });
        
        // Update sidebar navigation links
        const sidebarNavLinks = this.findAll('.sidebar-nav-link');
        sidebarNavLinks.forEach(link => {
            const view = link.dataset.view;
            const icon = link.querySelector('svg');
            
            if (view === this.currentView) {
                link.classList.add('text-blue-600', 'dark:text-blue-400', 'bg-blue-50', 'dark:bg-blue-900');
                link.classList.remove('text-gray-600', 'dark:text-gray-200', 'hover:bg-gray-50', 'dark:hover:bg-gray-700');
                
                if (icon) {
                    icon.classList.add('text-blue-600', 'dark:text-blue-400');
                    icon.classList.remove('text-gray-500', 'dark:text-gray-400', 'group-hover:text-gray-600', 'dark:group-hover:text-gray-300');
                }
            } else {
                link.classList.remove('text-blue-600', 'dark:text-blue-400', 'bg-blue-50', 'dark:bg-blue-900');
                link.classList.add('text-gray-600', 'dark:text-gray-200', 'hover:bg-gray-50', 'dark:hover:bg-gray-700');
                
                if (icon) {
                    icon.classList.remove('text-blue-600', 'dark:text-blue-400');
                    icon.classList.add('text-gray-500', 'dark:text-gray-400', 'group-hover:text-gray-600', 'dark:group-hover:text-gray-300');
                }
            }
        });
    }
    
    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
        const lightIcon = this.find('#theme-toggle-light-icon');
        const darkIcon = this.find('#theme-toggle-dark-icon');
        
        if (this.darkMode) {
            document.documentElement.classList.add('dark');
            lightIcon.classList.add('hidden');
            darkIcon.classList.remove('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            lightIcon.classList.remove('hidden');
            darkIcon.classList.add('hidden');
        }
        
        // Save preference to localStorage
        localStorage.setItem('darkMode', this.darkMode);
    }
    
    /**
     * Initialize dark mode based on system preference or saved preference
     */
    initDarkMode() {
        // Check for saved preference
        const savedPreference = localStorage.getItem('darkMode');
        
        if (savedPreference !== null) {
            this.darkMode = savedPreference === 'true';
        }
        
        this.toggleDarkMode();
    }
    
    /**
     * Load projects for the sidebar
     */
    async loadProjects() {
        try {
            const projects = await Storage.getAll('projects');
            
            // Update the sidebar projects list
            const projectsList = this.find('#sidebar-projects-list');
            
            if (projects.length === 0) {
                projectsList.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 text-center py-2">No projects yet</p>';
                return;
            }
            
            // Sort projects by name
            projects.sort((a, b) => a.name.localeCompare(b.name));
            
            // Generate HTML
            let html = '';
            projects.forEach(project => {
                html += `
                    <a href="#/projects/${project.id}" class="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700">
                        <span class="w-2 h-2 mr-3 rounded-full" style="background-color: ${project.color || '#3b82f6'}"></span>
                        ${project.name}
                    </a>
                `;
            });
            
            projectsList.innerHTML = html;
        } catch (error) {
            console.error('Failed to load projects', error);
            Toast.error('Failed to load projects. Please try again later.');
        }
    }
    
    /**
     * Open the new task modal
     */
    openNewTaskModal() {
        const modal = this.find('#new-task-modal');
        const modalContent = this.find('#new-task-modal-content');
        
        // Show the modal
        modal.classList.remove('hidden');
        
        // Load the task form content
        modalContent.innerHTML = `
            <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 class="text-lg leading-6 font-medium">Create New Task</h3>
                <form id="new-task-form" class="mt-4">
                    <div class="mb-4">
                        <label for="task-title" class="block text-sm font-medium mb-1">Title</label>
                        <input type="text" id="task-title" name="title" class="glass dark:glass-dark w-full rounded-md py-2 px-3" placeholder="Task title" required>
                    </div>
                    
                    <div class="mb-4">
                        <label for="task-description" class="block text-sm font-medium mb-1">Description</label>
                        <textarea id="task-description" name="description" class="glass dark:glass-dark w-full rounded-md py-2 px-3 h-24" placeholder="Task description"></textarea>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label for="task-project" class="block text-sm font-medium mb-1">Project</label>
                            <select id="task-project" name="project" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                <option value="">None</option>
                                <!-- Projects will be loaded here -->
                            </select>
                        </div>
                        
                        <div>
                            <label for="task-priority" class="block text-sm font-medium mb-1">Priority</label>
                            <select id="task-priority" name="priority" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                <option value="low">Low</option>
                                <option value="medium" selected>Medium</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label for="task-assignee" class="block text-sm font-medium mb-1">Assign To</label>
                            <select id="task-assignee" name="assignee" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                                <option value="">Unassigned</option>
                                <option value="current-user">Jordan</option>
                                <option value="pip">Pip</option>
                            </select>
                        </div>
                        
                        <div>
                            <label for="task-due-date" class="block text-sm font-medium mb-1">Due Date</label>
                            <input type="date" id="task-due-date" name="dueDate" class="glass dark:glass-dark w-full rounded-md py-2 px-3">
                        </div>
                    </div>
                </form>
            </div>
            <div class="px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button type="button" id="save-task-btn" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm">
                    Create Task
                </button>
                <button type="button" id="cancel-task-btn" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-700 text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                    Cancel
                </button>
            </div>
        `;
        
        // Load projects for the dropdown
        this.loadProjectsForDropdown();
        
        // Set today as the minimum date for due date
        const today = new Date().toISOString().split('T')[0];
        this.find('#task-due-date').min = today;
        
        // Set up event listeners
        this.on('#cancel-task-btn', 'click', () => {
            modal.classList.add('hidden');
        });
        
        this.on('#save-task-btn', 'click', () => {
            const form = this.find('#new-task-form');
            if (form.checkValidity()) {
                this.saveNewTask();
            } else {
                form.reportValidity();
            }
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
    
    /**
     * Load projects for the task form dropdown
     */
    async loadProjectsForDropdown() {
        try {
            const projects = await Storage.getAll('projects');
            const dropdown = this.find('#task-project');
            
            // Sort projects by name
            projects.sort((a, b) => a.name.localeCompare(b.name));
            
            // Generate options
            let options = '<option value="">None</option>';
            projects.forEach(project => {
                options += `<option value="${project.id}">${project.name}</option>`;
            });
            
            dropdown.innerHTML = options;
        } catch (error) {
            console.error('Failed to load projects for dropdown', error);
        }
    }
    
    /**
     * Save a new task
     */
    async saveNewTask() {
        try {
            const titleInput = this.find('#task-title');
            const descriptionInput = this.find('#task-description');
            const projectInput = this.find('#task-project');
            const priorityInput = this.find('#task-priority');
            const assigneeInput = this.find('#task-assignee');
            const dueDateInput = this.find('#task-due-date');
            
            const task = {
                id: `task-${Date.now()}`,
                title: titleInput.value.trim(),
                description: descriptionInput.value.trim(),
                status: 'inbox',
                priority: priorityInput.value,
                projectId: projectInput.value || null,
                assigneeId: assigneeInput.value || null,
                dueDate: dueDateInput.value || null,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            await Storage.save('tasks', task);
            
            // Close the modal
            this.find('#new-task-modal').classList.add('hidden');
            
            // Show success toast
            Toast.success('Task created successfully');
            
            // Notify the app about the new task
            EventBus.emit(Events.TASK_CREATED, task);
        } catch (error) {
            console.error('Failed to save task', error);
            Toast.error('Failed to create task. Please try again.');
        }
    }
    
    /**
     * Open the new project modal
     */
    openNewProjectModal() {
        // Similar implementation to openNewTaskModal
        // Creating a new project form and handling submission
    }
    
    /**
     * Export data as JSON file
     */
    async exportData() {
        try {
            const backup = await Storage.createBackup();
            
            if (!backup) {
                Toast.error('Failed to create backup');
                return;
            }
            
            // Create a download link
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(backup, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "mission-control-backup.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
            
            Toast.success('Data exported successfully');
        } catch (error) {
            console.error('Failed to export data', error);
            Toast.error('Failed to export data. Please try again.');
        }
    }
}

// Register the component globally
window.AppShell = AppShell;