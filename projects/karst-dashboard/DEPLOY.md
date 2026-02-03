# Quick Deployment Guide

## Step-by-Step Deployment to Vercel

### 1. Configure the Dashboard

First, update the configuration in `app.js`:

```javascript
const CONFIG = {
    GITHUB_REPO: 'KarstAgent/openclaw-workspace', // Your GitHub repo
    GITHUB_BRANCH: 'main',
    PASSWORD: 'karst2026', // Change this!
};
```

**⚠️ IMPORTANT:** Make sure your GitHub repo is public, or the dashboard won't be able to fetch data.

### 2. Test Locally

```bash
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard
python3 -m http.server 8080
```

Open http://localhost:8080 and test with password: `karst2026`

### 3. Create GitHub Repo

```bash
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Karst Dashboard"

# Create GitHub repo and push
gh repo create karst-dashboard --public --source=. --remote=origin --push
```

Alternatively, create manually:
1. Go to https://github.com/new
2. Name: `karst-dashboard`
3. Public repository
4. Don't initialize with README
5. Create repository
6. Follow push instructions

### 4. Deploy to Vercel

#### Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI if not installed
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (your account)
# - Link to existing project? N
# - What's your project's name? karst-dashboard
# - In which directory is your code located? ./
# - Want to modify these settings? N

# Deploy to production
vercel --prod
```

#### Using Vercel Web UI

1. Go to https://vercel.com/new
2. Import Git Repository
3. Select your `karst-dashboard` repo
4. Configure:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. Click **Deploy**

### 5. Set Custom Domain

After deployment:

1. Go to your project on Vercel
2. Settings → Domains
3. Add domain: `karst-dashboard.vercel.app`

Your dashboard will be live at: **https://karst-dashboard.vercel.app**

### 6. Enable Password Protection (Optional but Recommended)

For better security, use Vercel's built-in password protection:

1. Go to your project on Vercel
2. Settings → Deployment Protection
3. Enable "Password Protection"
4. Set a password
5. Save

This adds server-side authentication on top of the client-side check.

## Continuous Deployment

Once deployed, every push to your GitHub repo will automatically redeploy the dashboard.

```bash
# Make changes
git add .
git commit -m "Update dashboard"
git push

# Vercel will auto-deploy
```

## Troubleshooting

### GitHub API Rate Limiting

If you hit rate limits (60 requests/hour), add a GitHub token:

1. Create token: https://github.com/settings/tokens
   - Scopes: `public_repo` (or `repo` for private repos)
2. Update `app.js`:
   ```javascript
   async function fetchGitHubFile(path) {
       const url = `https://api.github.com/repos/${CONFIG.GITHUB_REPO}/contents/${path}`;
       const response = await fetch(url, {
           headers: {
               'Authorization': 'token YOUR_GITHUB_TOKEN'
           }
       });
       // ...
   }
   ```

### Private Repository

If your workspace repo is private:

1. Create GitHub Personal Access Token with `repo` scope
2. Add to all fetch calls in `app.js`
3. **⚠️ Security:** Store token as Vercel environment variable, not in code

## Quick Commands

```bash
# Test locally
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard
python3 -m http.server 8080

# Deploy to Vercel
vercel --prod

# View logs
vercel logs

# Remove deployment
vercel rm karst-dashboard
```

## Next Steps

After deployment:
- [ ] Test dashboard live
- [ ] Change default password
- [ ] Enable Vercel password protection
- [ ] Set up custom domain (optional)
- [ ] Add GitHub token if needed (rate limits)
- [ ] Share link with team
