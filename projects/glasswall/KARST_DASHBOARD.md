# Karst Agent Dashboard

Real-time monitoring dashboard for Karst agent activity, tasks, memory, and system status.

## Location

`/karst-dashboard` - Integrated into GlassWall Next.js app

## Features

### MVP (Implemented)

✅ **Task Monitoring**
- Active tasks with model, label, ETA, scope
- Completed tasks with duration and deliverables
- Real-time updates every 10 seconds

✅ **Session Info**
- Current model and thinking level
- System uptime
- Live status display

✅ **Heartbeat Status**
- Last heartbeat timestamp
- Next heartbeat countdown
- Per-service check tracking (email, calendar, social, etc.)

✅ **Memory Dashboard**
- Recent memory file updates (last 10)
- File sizes and timestamps
- Live file activity tracking

✅ **File Activity Log**
- Recent git changes (last 20)
- File status (added/modified/deleted)
- Timestamps and sizes

✅ **Real-Time Updates**
- Auto-refresh every 10 seconds
- Live countdown timers
- Responsive mobile-first design

### API Endpoints

**GET /api/karst/status**
Returns aggregated dashboard data:
```json
{
  "tasks": {
    "active": [...],
    "queued": [],
    "completed": [...]
  },
  "heartbeat": {
    "lastHeartbeat": "2026-02-03T13:16:00.000Z",
    "nextHeartbeat": "2026-02-03T13:46:00.000Z",
    "lastChecks": { "email": 1770121005, ... },
    "alerts": []
  },
  "memory": {
    "recentFiles": [...],
    "todayPreview": "..."
  },
  "files": [...],
  "session": {
    "model": "claude-sonnet-4-5",
    "thinking": "high",
    "uptime": 12345
  },
  "timestamp": "2026-02-03T13:31:00.000Z"
}
```

**POST /api/karst/actions**
Trigger manual actions:
```json
{
  "action": "read_file" | "trigger_heartbeat" | "list_memory",
  "params": { ... }
}
```

## Data Sources

- **TASKS.md** - Task queue and status
- **memory/heartbeat-state.json** - Heartbeat tracking
- **memory/*.md** - Daily logs and memory files
- **git log** - Recent file changes
- **process.uptime()** - Session runtime

## Configuration

Add to `.env.local`:
```bash
WORKSPACE_ROOT=/Users/karst/.openclaw/workspace
```

## Design

- **Dark mode** - Black background with colored accents
- **Mobile-first** - Responsive grid layout
- **Information density** - Compact but readable
- **Real-time** - 10-second polling interval
- **Fast** - < 1s page load

## Future Enhancements

🔜 **Sub-Agent Monitor**
- Live sub-agent list with session keys
- Token consumption and cost tracking
- Kill/restart controls

🔜 **Cost Tracking**
- Token usage by model
- Daily/weekly cost breakdown
- Budget alerts

🔜 **Quick Actions Panel**
- Manual heartbeat trigger
- Read any memory file
- View task output files
- Session controls

🔜 **Authentication**
- Password or token-based access
- Restrict to authorized users only

🔜 **WebSocket Updates**
- Replace polling with live WebSocket connection
- Instant updates on task changes

🔜 **Task Management**
- Spawn new tasks from dashboard
- Adjust task priority
- View full task logs

## Usage

1. **Development:**
   ```bash
   cd /Users/karst/.openclaw/workspace/projects/glasswall/app
   npm run dev
   ```

2. **Visit:** http://localhost:3000/karst-dashboard

3. **Deploy:** Vercel auto-deploys from git push

## Mobile Access

The dashboard is fully responsive and works on mobile devices. Access from phone to monitor agent activity on the go.

## Security Note

⚠️ Currently no authentication. Add password protection before public deployment.

Suggested: Add middleware to check for auth token or password.

## Files Created

- `src/app/karst-dashboard/page.tsx` - Main dashboard UI
- `src/app/karst-dashboard/layout.tsx` - Layout metadata
- `src/app/api/karst/status/route.ts` - Status API endpoint
- `src/app/api/karst/actions/route.ts` - Actions API endpoint

## Dependencies

All existing dependencies are sufficient:
- Next.js 16.1.6
- React 19.2.3
- Tailwind CSS 4

No additional packages required for MVP.
