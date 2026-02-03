# 🚀 START HERE - Karst Dashboard

## Quick Deploy (3 Steps)

### 1. Configure
Edit `app.js` lines 2-10:
```javascript
GITHUB_REPO: 'KarstAgent/openclaw-workspace', // Your repo
PASSWORD: 'karst2026', // Change this!
```

### 2. Test Locally
```bash
python3 -m http.server 8080
```
Open http://localhost:8080

### 3. Deploy
```bash
./deploy.sh
```

**Done!** Dashboard live at: https://karst-dashboard.vercel.app

---

## What Is This?

A standalone dashboard for monitoring Karst agent activity:
- 🔄 Active & completed tasks
- 💓 Heartbeat countdown & service checks
- 🧠 Memory file updates
- 📁 Recent git commits
- 🔄 Auto-refresh every 10s
- 🔒 Password protected
- 📱 Mobile responsive

---

## Files Overview

**Core (3):**
- `index.html` - Dashboard UI
- `styles.css` - Dark mode design
- `app.js` - GitHub API + logic

**Config (3):**
- `vercel.json` - Deployment
- `package.json` - Metadata
- `.gitignore` - Git rules

**Docs (5):**
- `README.md` - Setup guide
- `DEPLOY.md` - Deployment steps
- `DELIVERY.md` - Feature summary
- `OVERVIEW.md` - Project overview
- `COMPLETE.md` - Task summary

**Scripts (1):**
- `deploy.sh` - Auto-deploy

---

## Read Next

1. **Quick start?** → This file (you're here!)
2. **How to deploy?** → `DEPLOY.md`
3. **What was built?** → `COMPLETE.md`
4. **Full docs?** → `README.md`

---

## One-Liner Deploy

```bash
cd /Users/karst/.openclaw/workspace/projects/karst-dashboard && ./deploy.sh
```

That's it! 🎉
