# TRACKING.md - Transparency & Monitoring

## Purpose
Maximum visibility into what I do, how much it costs, and what I'm accomplishing.

## Files

### `tracking/activity-log.jsonl`
Real-time activity log. Each line is a JSON event:
```json
{"timestamp":"ISO8601","event":"event_type","details":"description","cost":0.00}
```

### `tracking/cost-tracker.json`
Monthly token usage and cost tracking:
- Budget: $200/month target
- Real-time totals by session
- Model-specific breakdowns
- Alert thresholds

### `tracking/daily-summary.md`
Auto-generated each morning with:
- What I accomplished overnight
- Cost breakdown
- Decisions made
- Next priorities

## Morning Briefing

Every morning I'll generate a briefing with:
1. **Overnight work** - what got done
2. **Costs** - token usage vs budget
3. **Wins** - completed tasks
4. **Blockers** - anything stuck
5. **Today's plan** - what's next

## Budget Tracking

**Target:** <$200/month
**Models & costs:**
- Sonnet: $3/$15 per M tokens (default)
- Haiku: $0.25/$1.25 per M tokens (validation)
- Opus: $15/$75 per M tokens (complex reasoning only)

**Alerts:**
- Yellow: >$150 month-to-date
- Red: >$180 month-to-date

## How to Check Status

### Quick Commands (just ask me)
- "What's the status?" → I'll pull from STATUS.md
- "Show me costs" → I'll run cost calculator
- "Morning briefing" → I'll generate daily summary
- "What did you do?" → I'll summarize recent work

### Manual Scripts (if you want to check yourself)
```bash
# Quick dashboard view
~/. openclaw/workspace/scripts/dashboard.sh

# Detailed cost breakdown
node ~/.openclaw/workspace/scripts/cost-calculator.js

# Generate daily briefing
~/.openclaw/workspace/scripts/generate-briefing.sh
```

### Files to Check Directly
- `STATUS.md` - What I'm working on right now
- `tracking/activity-log.jsonl` - Real-time event log
- `tracking/cost-tracker.json` - Token/cost tracking
- `tracking/daily-briefing-YYYY-MM-DD.md` - Daily summaries

---

*This system ensures you always know what I'm doing and what it costs.*
