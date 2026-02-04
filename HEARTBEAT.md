# HEARTBEAT.md - Autonomous Agent Mode

## PRIMARY MISSION: GlassWall Product Development
**Role:** PM + CTO
**Mode:** Continuous autonomous building
**Model Strategy:** Use Haiku for routine work, Sonnet for building

**Progress Reporting (Every 5 Minutes):**

Format your update like this:
```
**Currently:** [What you're doing right now in plain English]
**Completed:** [What you just finished]
**Next:** [What's coming up after this]
**Why it matters:** [Brief explanation a non-technical person would understand]
```

Example:
```
**Currently:** Building the paid messaging database schema
**Completed:** Designed the payment verification flow 
**Next:** Deploy and test with a real transaction
**Why it matters:** This lets GlassWall agents charge for instant messages, so they can make money while helping users
```

**Rules:**
- Keep it conversational, not robotic
- Explain technical work in simple terms
- Only send updates when actively working (HEARTBEAT_OK when idle)
- Alert immediately for: shipped features, blockers, urgent decisions needed

## Current Status (As of 22:05 PST)
**Mission:** Build GlassWall into the best product possible - working all night
**Mode:** Autonomous building with 5-minute progress updates

**🚨 MODEL STRATEGY CHECK (Every Update):**
- Am I using OpenRouter for sub-agents? ✅ YES / ❌ NO
- Could this work be done by DeepSeek cheaper? ✅ YES / ❌ NO
- Am I following the model-strategy skill? ✅ YES / ❌ NO

**Progress Update #7:**
✅ Fixed AGENTS.md and HEARTBEAT.md to enforce model strategy
✅ Added mandatory model checks to prevent cost waste
✅ Working on agent settings page (profile editing)

**Shipped Features (COMPLETE):**
1. ✅ Dynamic homepage stats (live agent/message counts)
2. ✅ Enhanced agent directory (message count, join date, better UX)
3. ✅ Agent Dashboard (full stats, earnings tracking, recent messages)
4. ✅ Compelling landing page (better copy, value props, use cases)
5. ✅ SEO optimization (comprehensive meta tags for discoverability)
6. 🚧 Agent settings page (in progress)

**Working on next:** Commit settings page + test thoroughly with proper model usage

## Active Work (Check Every Heartbeat)
**CRITICAL: Use Haiku for all non-building work**
1. **First, read memory/current-work-status.md** - this has real-time work updates
2. If active work found, report status to user (don't say HEARTBEAT_OK)
3. If nothing active, check for: new emails, calendar events <2h, system issues
4. Spawn Haiku sub-agent only if needed for validation tasks

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
- Use qmd instead of reading full files
- DeepSeek makes frequent checks ultra-cheap ($0.14/1M)
- Target: <500 tokens per heartbeat = ~$0.0007 each (DeepSeek)
- Daily cost: ~288 heartbeats × $0.0007 = ~$0.20/day
- Frequent updates are now cost-effective!

---

**Current Status:** Active
**Check Frequency:** Every 5 minutes (configured in OpenClaw)
**Time Format:** 12-hour EST (e.g., 10:30 PM EST)
**Alert Policy:** 24/7 - No quiet hours
