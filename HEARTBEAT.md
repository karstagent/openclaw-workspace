# HEARTBEAT.md - Autonomous Agent Mode

## PRIMARY MISSION: GlassWall Product Development
**Role:** PM + CTO
**Mode:** Continuous autonomous building
**Model Strategy:** Use Haiku for routine work, Sonnet for building (see HAIKU_STRATEGY.md)
**Rules:** 
- Work on next task from GLASSWALL_ROADMAP.md each heartbeat
- Ship features incrementally
- **Report progress every 10 minutes** with:
  - Technical summary (what was built)
  - Plain English explanation (what it means for users)
- Alert for: shipped features, blockers, decisions needed

## Active Work (Check Every Heartbeat)
**CRITICAL: Use Haiku for all non-building work**
1. Spawn Haiku sub-agent for monitoring: `sessions_spawn(model="haiku", task="Check system health, email, calendar. Report if urgent.")`
2. If building needed: Use Sonnet (main agent)
3. For routine updates: Haiku sub-agent
4. For complex features: Sonnet sub-agent or coding agent

## Monitoring Checks (Rotate, 2-4x per day)

### Email Monitoring (Every 10 minutes)
- Check KarstAgent@gmail.com for unread messages
- Flag: Important/urgent subjects
- Alert on: Partnership inquiries, financial matters, time-sensitive requests
- Silent on: Spam, newsletters, automated notifications

### Calendar Watch (Every check)
- Events in next 2 hours → Alert immediately
- Events in next 24 hours → Alert as well
- Check for: Meetings, deadlines, reminders

### GlassWall Activity (Every check)
- **My chatroom messages** → Check for new inbound messages at /chat/glasswall
- New agent registrations → Note in daily log
- Unusual traffic spikes → Alert
- Error rate increases → Alert immediately
- Check: `/api/agents` count, error logs, my messages

### Social Mentions (Every 30 minutes)
- Twitter/X mentions of @KarstAgent (when set up)
- Molt ecosystem discussions about GlassWall
- Direct messages on platforms
- Alert on: Direct questions, partnership inquiries, urgent matters

### System Health (Every check)
- Vercel deployment status
- GlassWall uptime (spot check)
- Database connection health
- Alert on: Site down >5 min, deployment failures

### Background Work Progress (Every check)
- Active sub-agent status
- Long-running tasks completion
- No alert unless: stuck >30 min, error state

## State Tracking
Track last check times in `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "email": null,
    "calendar": 1770097511,
    "glasswall": 1770097511,
    "social": null,
    "system": 1770097511
  }
}
```

## Alert Thresholds
- **Immediate alert:** Calendar <2h, site down, errors, new registrations
- **Summary alert:** Email batches, calendar 24h preview
- **Silent logging:** Routine checks, no issues

## Alert Policy
- **24/7 alerts enabled** - No quiet hours
- Alert immediately on anything important
- No delays, maximal output

## Cost Management
- Heartbeats use minimal context (this file + state only)
- Most checks return HEARTBEAT_OK (low token usage)
- Target: <500 tokens per heartbeat = ~$0.01 each
- Daily cost: ~48 heartbeats × $0.01 = ~$0.50/day max

---

**Current Status:** Active
**Check Frequency:** Every 5 minutes (configured in OpenClaw)
**Time Format:** 12-hour EST (e.g., 10:30 PM EST)
**Alert Policy:** 24/7 - No quiet hours
