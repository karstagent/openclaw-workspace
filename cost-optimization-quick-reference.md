# OpenClaw Cost Optimization - Quick Reference

**TL;DR: Save 70-80% on agent costs with these strategies**

---

## Top 5 Quick Wins (Do These First)

### 1. Enable Session Pruning (5 minutes)
```json
{
  "agent": {
    "contextPruning": {
      "mode": "cache-ttl",
      "ttl": "5m"
    }
  }
}
```
**Savings: 20-40%**

### 2. Use Haiku for Validation (10 minutes)
```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-haiku-4": { "alias": "Haiku" }
      }
    }
  }
}
```
**Savings: 98% on validation tasks**

### 3. Install qmd (15 minutes)
```bash
npm install -g quick-markdown
cd ~/.openclaw/workspace
qmd update
```
**Savings: 94% on file reads**

### 4. Optimize Heartbeats (5 minutes)
```json
{
  "heartbeat": {
    "interval": "30m",
    "model": "anthropic/claude-haiku-4"
  }
}
```
**Savings: 50-70%**

### 5. Limit Group History (5 minutes)
```json
{
  "messages": {
    "groupChat": {
      "historyLimit": 20
    }
  }
}
```
**Savings: 80% in groups**

**Total time: 40 minutes**
**Total savings: 50-70%**

---

## Model Selection Cheat Sheet

| Task Type | Model | Cost/1M | Use When |
|-----------|-------|---------|----------|
| Validation | Haiku/DeepSeek | $0.25 | Checking format, simple yes/no |
| General | Sonnet-4 | $3 | Writing, coding, most tasks |
| Complex | Opus-4.5 | $15 | Architecture, debugging, stuck |

**Rule: Default to Sonnet, use Haiku for validation, escalate to Opus only when needed**

---

## File Access Pattern

### ❌ Bad
```typescript
const memory = await read("MEMORY.md");  // 10K tokens
```

### ✅ Good
```typescript
const relevant = await exec("qmd search 'recent tasks' -n 3");  // 600 tokens
```

**Savings: 94%**

---

## Heartbeat Pattern

### ❌ Bad
```markdown
# Every heartbeat:
- Read full MEMORY.md (10K tokens)
- Check email (full inbox scan)
- Check calendar (all events)
= 15K tokens per heartbeat
```

### ✅ Good
```markdown
# Batch and rotate checks:
- Use qmd search for quick checks (600 tokens)
- Only load full context if needed
- Batch related operations
- Return HEARTBEAT_OK when quiet
= 1-2K tokens per heartbeat
```

**Savings: 85%**

---

## Sub-Agent Strategy

### ✅ Always Use Sub-Agent (Cheap Model)
- Format validation
- Simple checks
- Data extraction
- Yes/no decisions

### 🤔 Consider Sub-Agent
- Risky operations (sandbox)
- Long research (don't block)
- Different model per step

### ❌ Stay in Main
- Need conversation context
- User waiting for response
- Quick single-step

---

## Configuration Template

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": ["anthropic/claude-haiku-4"]
      },
      "models": {
        "anthropic/claude-sonnet-4-5": { "alias": "Sonnet" },
        "anthropic/claude-opus-4-5": { "alias": "Opus" },
        "anthropic/claude-haiku-4": { "alias": "Haiku" }
      },
      "contextTokens": 100000,
      "bootstrapMaxChars": 10000
    }
  },
  "agent": {
    "contextPruning": {
      "mode": "cache-ttl",
      "ttl": "5m",
      "keepLastAssistants": 3
    }
  },
  "session": {
    "reset": {
      "mode": "daily",
      "atHour": 4,
      "idleMinutes": 120
    }
  },
  "heartbeat": {
    "interval": "30m",
    "model": "anthropic/claude-haiku-4"
  },
  "messages": {
    "groupChat": {
      "historyLimit": 20
    }
  },
  "tools": {
    "exec": {
      "maxOutputBytes": 50000
    },
    "read": {
      "maxChars": 50000
    },
    "web": {
      "search": {
        "cacheTtlMinutes": 60,
        "maxResults": 5
      },
      "fetch": {
        "cacheTtlMinutes": 60,
        "maxChars": 10000
      }
    }
  },
  "skills": {
    "allowBundled": ["essential-skill-1", "essential-skill-2"]
  }
}
```

---

## Cost Tracking

### Monitor These
```bash
# Session token usage
openclaw sessions --json | jq '.[] | {key: .sessionKey, tokens: .totalTokens}'

# Model distribution
openclaw status

# Daily costs
openclaw usage --daily
```

### Set Alerts
```json
{
  "monitoring": {
    "alerts": {
      "dailyCostThreshold": 100,
      "sessionTokenThreshold": 100000
    }
  }
}
```

---

## Common Mistakes

| ❌ Don't | ✅ Do |
|---------|-------|
| Use Opus for everything | Use model tiers |
| Read full files every time | Use qmd search |
| Heartbeat every 5 minutes | Heartbeat every 30-60 min |
| Include 500 group messages | Limit to 20-50 messages |
| Never prune sessions | Enable cache-ttl pruning |
| 10K token bootstrap files | 2K token concise files |

---

## Cost Impact Example

### Unoptimized Agent
- 1000 requests/day @ 50K tokens (Opus)
- Cost: **$750/day = $22,500/month**

### After Quick Wins (40 min setup)
- Session pruning + qmd + Haiku + heartbeat optimization
- Cost: **$300/day = $9,000/month**
- **Savings: $13,500/month (60%)**

### Fully Optimized
- All strategies implemented
- Cost: **$165/day = $4,950/month**
- **Total savings: $17,550/month (78%)**

---

## Next Steps

1. **Week 1:** Implement Quick Wins (40 minutes)
   - Enable session pruning
   - Add Haiku model
   - Install qmd
   - Optimize heartbeat
   - Limit group history

2. **Week 2-3:** Full optimization
   - Three-tier model strategy
   - qmd-first patterns
   - Workspace file optimization
   - Session policies
   - Skill audit

3. **Week 4+:** Advanced techniques
   - Smart sub-agent dispatching
   - Cron for batch operations
   - Tool usage patterns
   - Cost monitoring dashboard

---

## Resources

- **Full Guide:** See `openclaw-cost-optimization-guide.md`
- **Docs:** https://docs.openclaw.ai
- **Discord:** https://discord.gg/clawd
- **qmd:** `npm install -g quick-markdown`

---

**Start with the Quick Wins above and track your savings!**
