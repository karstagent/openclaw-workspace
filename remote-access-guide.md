# Remote Access Guide for Mission Control

## Overview
This guide provides comprehensive instructions for accessing the Mission Control dashboard, including the Kanban board, from any location. It covers both local network access and remote access via Vercel deployment.

## Access Methods

### 1. Local Network Access

#### Direct Local Access (Same Machine)
- **URL**: http://localhost:3002/dashboard/kanban
- **Requirements**: None
- **Notes**: Fastest performance, all features available

#### Local Network Access (Same Network)
- **URL**: http://[Mac mini IP address]:3002/dashboard/kanban
- **Requirements**: 
  - Being connected to the same network as the Mac mini
  - Mission Control server running on the Mac mini
- **Finding the IP address**:
  ```bash
  # On the Mac mini, run:
  ifconfig | grep "inet " | grep -v 127.0.0.1
  ```
- **Notes**: Good performance, all features available

#### Port Forwarding (Advanced)
- **Setup**:
  1. Configure your router to forward port 3002 to the Mac mini's local IP address
  2. Use a dynamic DNS service if you don't have a static IP
  3. Access via http://[your-public-ip]:3002/dashboard/kanban
- **Security Note**: Consider adding basic authentication if using port forwarding

### 2. Vercel Deployment (Recommended for Remote Access)

#### Production Deployment
- **URL**: https://mission-control-dashboard.vercel.app
- **Requirements**: Internet connection
- **Features**: 
  - Full Liquid Glass UI
  - Real-time updates
  - Mobile-responsive interface
  - Secure HTTPS connection
- **Authentication**: Uses the same credentials as the local version

#### Preview Deployments
For testing new features before they go live:
- **URL Pattern**: https://mission-control-dashboard-[branch-name].vercel.app
- **Current Preview**: https://mission-control-dashboard-fix-styling.vercel.app

### 3. SSH Tunneling (Advanced Technical Users)

If you need secure access to the local version from anywhere:

```bash
# On your remote machine:
ssh -L 3002:localhost:3002 username@mac-mini-ip-address

# Then access in your browser:
http://localhost:3002/dashboard/kanban
```

## Authentication

### Local Development
- No authentication required by default
- Can be enabled by setting `ENABLE_AUTH=true` in `.env.local`

### Vercel Deployment
- Uses NextAuth.js for secure authentication
- Supports:
  - Email/Password
  - GitHub OAuth
  - Google OAuth

## Troubleshooting

### Local Access Issues
1. **Cannot connect to localhost:3002**
   - Ensure Mission Control is running: `cd /Users/karst/.openclaw/workspace && ./check_mission_control.sh`
   - If not running, start it: `./start_mission_control.sh`

2. **Cannot connect from another device on the network**
   - Verify both devices are on the same network
   - Check if firewall is blocking port 3002
   - Try using the IP address directly

### Remote Access Issues
1. **CSS/Styling looks different**
   - Clear browser cache
   - Try a different browser
   - Use the most recent deployment URL

2. **Cannot login to remote deployment**
   - Check that you're using the correct credentials
   - Ensure cookies are enabled in your browser
   - Try incognito/private browsing mode

3. **Slow performance**
   - Remote access may be slower than local, especially for large boards
   - Try reducing the number of tasks displayed
   - Use the "compact view" option for better performance

## Feature Differences

| Feature | Local | Vercel Deployment |
|---------|-------|-------------------|
| UI Styling | Full Liquid Glass | Full Liquid Glass |
| Update Speed | Real-time | Real-time |
| Data Storage | Local JSON files | Cloud database |
| Authentication | Optional | Required |
| Offline Mode | Available | Not available |

## Keeping Remote Access Secure

1. Use strong, unique passwords for authentication
2. Don't share access URLs publicly
3. Regularly check active sessions
4. Log out when finished on shared or public devices
5. Consider using a VPN for additional security

## Getting Help

If you encounter issues not covered in this guide:
- Check the logs: `/Users/karst/.openclaw/workspace/logs/mission_control.log`
- Review recent deployment status: `/Users/karst/.openclaw/workspace/logs/deployment.log`
- Contact system administrator for assistance

---

*This guide will be updated as new access methods become available.*