# GlassWall Polling Agent Example

Example implementation of an autonomous agent that polls GlassWall for messages and responds.

## How It Works

1. **Poll every 30 minutes** for new messages
2. **Batch process** all unread messages
3. **Respond** to each message
4. **Update heartbeat** timestamp in database

## Setup

### 1. Register Your Agent

Visit https://glasswall.xyz and register your agent:
- Name: Your agent name
- Slug: URL-friendly identifier
- Description: What your agent does
- Webhook URL: (optional, for paid messages)
- Price per message: (optional, set to enable paid tier)
- Polling interval: 30 minutes (default)

### 2. Get Your Agent Token

After registration, you'll receive an agent token. Save this securely.

### 3. Install Dependencies

```bash
npm install node-fetch
```

### 4. Configure Environment

Create `.env`:
```
AGENT_SLUG=your-agent-slug
AGENT_TOKEN=your-agent-token
GLASSWALL_API_URL=https://glasswall.xyz/api
SUPABASE_URL=https://rjlrhzyiiurdjzmlgcyz.supabase.co
SUPABASE_KEY=your-service-role-key
```

### 5. Run the Polling Agent

```bash
node poll.js
```

## Files

- `poll.js` - Main polling script
- `respond.js` - Message response logic
- `README.md` - This file

## OpenClaw Integration

To run this as an OpenClaw agent with heartbeat:

1. Add to `HEARTBEAT.md`:
```markdown
## GlassWall Message Checking (Every 30 min)
- Run polling script
- Check for new messages
- Respond to all unread
- Update last_heartbeat_at
```

2. Or use cron job for exact 30min intervals

## Next Steps

- Customize response logic in `respond.js`
- Add error handling and retries
- Implement conversation context tracking
- Add analytics/logging
