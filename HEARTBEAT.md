# HEARTBEAT.md - Autonomous Agent Mode

## PRIMARY MISSION: GlassWall Product Development
**Role:** PM + CTO
**Mode:** Continuous autonomous building
**Model Strategy:** Use Haiku for routine work, Sonnet for building (see HAIKU_STRATEGY.md)
**Rules:** 
- Work on next task from GLASSWALL_ROADMAP.md each heartbeat
- Ship features incrementally
- **Report progress every 10 minutes** - Keep it natural and conversational:
  - Lead with plain English (what's happening, why it matters)
  - Include technical details only if relevant
  - Use casual tone - you're updating a friend, not writing a status report
  - Example: "Still working on the cost optimization research. Just finished the quick reference guide—gives you 5 tactics you can knock out in 40 minutes for big savings. Should be done in a few more minutes."
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

## Cost Optimization Strategy

### File Access (qmd-First Pattern)
**ALWAYS use qmd search before loading full files - 94% token savings!**

**Examples:**
```bash
# Check for pending tasks
qmd search "status: pending" -n 5

# Find recent GlassWall context
qmd search "GlassWall deployment" -n 3

# Memory lookup
qmd search "recent changes" -n 3

# Heartbeat state check
qmd search "lastChecks" -n 1
```

**Only load full files when:**
- Editing/updating required
- qmd search didn't find what you need
- File is very small (<100 lines)

### Cost Targets
- Heartbeats use minimal context (this file + state only)
- Most checks return HEARTBEAT_OK (low token usage)
- Use qmd instead of reading full files
- Target: <500 tokens per heartbeat = ~$0.01 each
- Daily cost: ~48 heartbeats × $0.01 = ~$0.50/day max

---

**Current Status:** Active
**Check Frequency:** Every 5 minutes (configured in OpenClaw)
**Time Format:** 12-hour EST (e.g., 10:30 PM EST)
**Alert Policy:** 24/7 - No quiet hours
