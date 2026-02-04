// Configuration
const CONFIG = {
    // GitHub API endpoints
    GITHUB_REPO: 'karstagent/openclaw-workspace', // Change this to your actual repo
    GITHUB_BRANCH: 'main',
    
    // Files to fetch
    FILES: {
        TASKS: 'TASKS.md',
        HEARTBEAT: 'memory/heartbeat-state.json',
    },
    
    // Update interval (ms) - 10 seconds for real-time monitoring
    REFRESH_INTERVAL: 10000,
    
    // Password (stored in localStorage after first auth)
    PASSWORD: 'karst2026', // Change this!
};

// State
let refreshTimer = null;
let countdownTimer = null;
let isAuthenticated = false;

// Authentication
function authenticate() {
    const input = document.getElementById('password-input');
    const error = document.getElementById('auth-error');
    const password = input.value.trim();
    
    if (password === CONFIG.PASSWORD) {
        localStorage.setItem('karst_auth', 'true');
        isAuthenticated = true;
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
        init();
    } else {
        error.textContent = 'Invalid password';
        input.value = '';
    }
}

// Check auth on load
function checkAuth() {
    if (localStorage.getItem('karst_auth') === 'true') {
        isAuthenticated = true;
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
        init();
    }
}

// Initialize dashboard
function init() {
    updateDashboard();
    startRefreshTimer();
    startCountdownTimer();
}

// Fetch data from GitHub
async function fetchGitHubFile(path) {
    try {
        const url = `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/contents/${path}?ref=${CONFIG.GITHUB_BRANCH}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status}`);
        }
        
        const data = await response.json();
        const content = atob(data.content); // Decode base64
        return content;
    } catch (error) {
        console.error(`Error fetching ${path}:`, error);
        return null;
    }
}

// Fetch recent commits
async function fetchRecentCommits() {
    try {
        const url = `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/commits?per_page=10`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching commits:', error);
        return [];
    }
}

// Parse TASKS.md
function parseTasks(markdown) {
    if (!markdown) return { active: [], completed: [] };
    
    const active = [];
    const completed = [];
    
    const activeSection = markdown.match(/## 🔄 Active Tasks\n([\s\S]*?)\n## /);
    const completedSection = markdown.match(/## ✅ Completed Tasks\n([\s\S]*?)\n## /);
    
    // Parse active tasks
    if (activeSection) {
        const taskBlocks = activeSection[1].split(/\n### \d+\. /).filter(b => b.trim());
        taskBlocks.forEach(block => {
            const lines = block.split('\n');
            const title = lines[0].trim();
            const status = (lines.find(l => l.includes('**Status:**')) || '').replace(/\*\*Status:\*\*\s*/, '').trim();
            const model = (lines.find(l => l.includes('**Model:**')) || '').replace(/\*\*Model:\*\*\s*/, '').trim();
            const eta = (lines.find(l => l.includes('**ETA:**')) || '').replace(/\*\*ETA:\*\*\s*/, '').trim();
            const label = (lines.find(l => l.includes('**Label:**')) || '').replace(/\*\*Label:\*\*\s*/, '').trim();
            
            const scopeStart = lines.findIndex(l => l.includes('**Scope:**'));
            const scope = scopeStart > -1 ? lines.slice(scopeStart + 1).filter(l => l.trim().startsWith('-')).map(l => l.trim().substring(2)).join('\n') : '';
            
            active.push({ title, status, model, eta, label, scope });
        });
    }
    
    // Parse completed tasks (last 5)
    if (completedSection) {
        const taskBlocks = completedSection[1].split(/\n### \d+\. /).filter(b => b.trim()).slice(0, 5);
        taskBlocks.forEach(block => {
            const lines = block.split('\n');
            const title = lines[0].trim();
            const completed = (lines.find(l => l.includes('**Completed:**')) || '').replace(/\*\*Completed:\*\*\s*/, '').trim();
            const model = (lines.find(l => l.includes('**Model:**')) || '').replace(/\*\*Model:\*\*\s*/, '').trim();
            const deliverables = lines.filter(l => l.trim().startsWith('- ✅')).map(l => l.trim().substring(4));
            
            completed.push({ title, completed, model, deliverables });
        });
    }
    
    return { active, completed };
}

// Update dashboard
async function updateDashboard() {
    const now = new Date();
    document.getElementById('last-update').textContent = `Last updated: ${now.toLocaleTimeString()}`;
    
    // Session info (static for now)
    document.getElementById('model').textContent = 'Claude Sonnet 4.5';
    document.getElementById('runtime').textContent = 'OpenClaw Agent';
    document.getElementById('status').textContent = 'Online';
    
    // Fetch tasks
    const tasksMarkdown = await fetchGitHubFile(CONFIG.FILES.TASKS);
    const tasks = parseTasks(tasksMarkdown);
    
    // Render active tasks
    const activeTasks = document.getElementById('active-tasks');
    if (tasks.active.length > 0) {
        activeTasks.innerHTML = tasks.active.map(task => `
            <div class="task-item">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <span class="badge badge-progress">${task.status}</span>
                </div>
                <div class="task-meta">
                    <span>🤖 ${task.model}</span>
                    <span>⏱️ ${task.eta}</span>
                    ${task.label ? `<span>🏷️ ${task.label}</span>` : ''}
                </div>
                ${task.scope ? `<div class="task-scope"><strong>Scope:</strong><ul>${task.scope.split('\n').map(s => `<li>${s}</li>`).join('')}</ul></div>` : ''}
            </div>
        `).join('');
    } else {
        activeTasks.innerHTML = '<p class="empty-state">No active tasks</p>';
    }
    
    // Render completed tasks
    const completedTasks = document.getElementById('completed-tasks');
    if (tasks.completed.length > 0) {
        completedTasks.innerHTML = tasks.completed.map(task => `
            <div class="task-item">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <span class="badge badge-completed">Completed</span>
                </div>
                <div class="task-meta">
                    <span>⏰ ${task.completed}</span>
                    <span>🤖 ${task.model}</span>
                </div>
                ${task.deliverables.length > 0 ? `<div class="task-scope"><strong>Deliverables:</strong><ul>${task.deliverables.map(d => `<li>${d}</li>`).join('')}</ul></div>` : ''}
            </div>
        `).join('');
    } else {
        completedTasks.innerHTML = '<p class="empty-state">No completed tasks</p>';
    }
    
    // Fetch heartbeat
    const heartbeatJson = await fetchGitHubFile(CONFIG.FILES.HEARTBEAT);
    if (heartbeatJson) {
        const heartbeat = JSON.parse(heartbeatJson);
        const lastHeartbeat = new Date(heartbeat.lastHeartbeat);
        document.getElementById('last-heartbeat').textContent = lastHeartbeat.toLocaleString();
        
        // Update checks
        Object.keys(heartbeat.lastChecks).forEach(key => {
            const el = document.getElementById(`check-${key}`);
            if (el) {
                const timestamp = heartbeat.lastChecks[key];
                const date = new Date(timestamp * 1000);
                el.textContent = timeAgo(date);
            }
        });
    }
    
    // Fetch recent commits
    const commits = await fetchRecentCommits();
    const fileChanges = document.getElementById('file-changes');
    if (commits.length > 0) {
        fileChanges.innerHTML = `
            <div class="file-list">
                ${commits.slice(0, 10).map(commit => `
                    <div class="file-item">
                        <div class="file-name">${escapeHtml(commit.commit.message)}</div>
                        <div class="file-commit">${commit.sha.substring(0, 7)} • ${timeAgo(new Date(commit.commit.author.date))}</div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        fileChanges.innerHTML = '<p class="empty-state">No recent commits</p>';
    }
    
    // Memory activity (list recent memory files from commits)
    const memoryCommits = commits.filter(c => c.commit.message.toLowerCase().includes('memory') || c.files?.some(f => f.filename.includes('memory/')));
    const memoryActivity = document.getElementById('memory-activity');
    if (memoryCommits.length > 0) {
        memoryActivity.innerHTML = `
            <div class="memory-list">
                ${memoryCommits.slice(0, 5).map(commit => `
                    <div class="memory-item">
                        <div class="memory-name">${escapeHtml(commit.commit.message)}</div>
                        <div class="memory-time">${timeAgo(new Date(commit.commit.author.date))}</div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        memoryActivity.innerHTML = '<p class="empty-state">No recent memory activity</p>';
    }
}

// Countdown to next heartbeat
function startCountdownTimer() {
    if (countdownTimer) clearInterval(countdownTimer);
    
    countdownTimer = setInterval(() => {
        const lastHeartbeat = document.getElementById('last-heartbeat').textContent;
        if (lastHeartbeat !== '-') {
            const lastTime = new Date(lastHeartbeat);
            const nextHeartbeat = new Date(lastTime.getTime() + 30 * 60 * 1000); // 30 min
            const now = new Date();
            const diff = nextHeartbeat - now;
            
            if (diff > 0) {
                const minutes = Math.floor(diff / 60000);
                const seconds = Math.floor((diff % 60000) / 1000);
                document.getElementById('heartbeat-countdown').textContent = `${minutes}m ${seconds}s`;
            } else {
                document.getElementById('heartbeat-countdown').textContent = 'Overdue';
            }
        }
    }, 1000);
}

// Refresh timer
function startRefreshTimer() {
    let countdown = CONFIG.REFRESH_INTERVAL / 1000;
    
    if (refreshTimer) clearInterval(refreshTimer);
    
    refreshTimer = setInterval(() => {
        countdown--;
        document.getElementById('next-refresh').textContent = `Next refresh: ${countdown}s`;
        
        if (countdown <= 0) {
            updateDashboard();
            countdown = CONFIG.REFRESH_INTERVAL / 1000;
        }
    }, 1000);
}

// Utility: time ago
function timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// Utility: escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle password input enter key
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password-input');
    if (passwordInput) {
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                authenticate();
            }
        });
    }
    
    checkAuth();
});
