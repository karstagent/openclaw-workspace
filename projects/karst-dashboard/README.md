# Karst Dashboard

A lightweight, standalone dashboard for monitoring Karst agent activity in real-time.

## Features

- 🔄 **Task Monitoring** - Active and completed tasks with progress
- 💓 **Heartbeat Monitor** - Live countdown and service check timestamps
- 🧠 **Memory Activity** - Recent memory file updates
- 📁 **File Changes** - Recent git commits
- 📊 **Session Info** - Current model and runtime status
- 🔄 **Auto-refresh** - Updates every 10 seconds
- 🔒 **Password Protected** - Simple authentication
- 🌙 **Dark Mode** - Easy on the eyes
- 📱 **Mobile Responsive** - Works on all devices

## Tech Stack

- Pure HTML/CSS/JavaScript (no build process!)
- GitHub API for data fetching
- Vercel for deployment

## Setup & Deployment

### 1. Configure GitHub Repo

Edit `app.js` and update the GitHub configuration:

```javascript
const CONFIG = {
    GITHUB_REPO: 'YourUsername/your-repo', // Change this!
    GITHUB_BRANCH: 'main',
    PASSWORD: 'your-secure-password', // Change this!
};
```

**Important:** Make sure your GitHub repo is **public** or configure a personal access token for private repos.

### 2. Local Testing

Simply open `index.html` in a browser:

```bash
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard
open index.html
```

Or use a local server:

```bash
python3 -m http.server 8080
# Open http://localhost:8080
```

Default password: `karst2026`

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Navigate to project
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - What's your project name? karst-dashboard
# - What directory is your code in? ./
# - Override settings? No

# For production deployment
vercel --prod
```

#### Option B: Using Vercel Web UI

1. Push code to GitHub:
   ```bash
   cd /Users/karst/.openclaw/workspace/projects/karst-dashboard
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create karst-dashboard --public --source=. --remote=origin --push
   ```

2. Go to [vercel.com](https://vercel.com)
3. Click "Add New Project"
4. Import your GitHub repo
5. Project name: `karst-dashboard`
6. Framework Preset: `Other`
7. Root Directory: `./`
8. Build Command: (leave empty)
9. Output Directory: (leave empty)
10. Click "Deploy"

#### Option C: Using Vercel GitHub Integration

1. Connect Vercel to your GitHub account
2. Push to GitHub
3. Vercel will auto-deploy on every push

### 4. Custom Domain (Optional)

After deployment, set up custom domain:

1. Go to your Vercel project settings
2. Click "Domains"
3. Add domain: `karst-dashboard.vercel.app` (or your custom domain)
4. Follow DNS configuration if using custom domain

## Configuration

### Change Password

Edit `app.js`:

```javascript
const CONFIG = {
    PASSWORD: 'your-new-password', // Change this!
};
```

**Note:** This is client-side authentication (not super secure). For production, consider:
- Using Vercel's password protection (Project Settings → Password Protection)
- Implementing server-side auth with Vercel Edge Functions
- Using OAuth/JWT

### Change GitHub Repo

Edit `app.js`:

```javascript
const CONFIG = {
    GITHUB_REPO: 'YourUsername/your-repo',
    GITHUB_BRANCH: 'main', // or your default branch
};
```

### Adjust Refresh Rate

Edit `app.js`:

```javascript
const CONFIG = {
    REFRESH_INTERVAL: 10000, // milliseconds (10 seconds)
};
```

## Data Sources

The dashboard fetches data from:

1. **TASKS.md** - Task status and progress
2. **memory/heartbeat-state.json** - Heartbeat and service checks
3. **Git commits** - File activity and memory updates

All data is fetched from your GitHub repo via the GitHub API.

## File Structure

```
karst-dashboard/
├── index.html          # Main dashboard page
├── styles.css          # Dark mode styling
├── app.js              # Dashboard logic & GitHub API
├── vercel.json         # Deployment config
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Troubleshooting

### Dashboard shows "No data"

- Check GitHub repo is public (or add access token)
- Verify `GITHUB_REPO` is correct in `app.js`
- Check browser console for API errors
- Ensure TASKS.md and heartbeat-state.json exist in repo

### Authentication not working

- Clear localStorage: `localStorage.clear()`
- Check password in `app.js`
- Try incognito/private browsing

### Rate limiting

GitHub API has rate limits (60 req/hour for unauthenticated). To increase:

1. Create a GitHub Personal Access Token
2. Add to fetch headers in `app.js`:
   ```javascript
   headers: {
       'Authorization': 'token YOUR_GITHUB_TOKEN'
   }
   ```

## Security Notes

⚠️ **Current authentication is basic client-side protection**

For production use:
- Enable Vercel password protection
- Use environment variables for sensitive data
- Implement server-side authentication
- Don't expose private data in public repos

## License

MIT

## Support

For issues or questions, contact the Karst team.
