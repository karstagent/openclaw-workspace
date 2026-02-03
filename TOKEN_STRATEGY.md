# TOKEN STRATEGY - Cost Reduction Best Practices

**Goal:** Reduce token burn by 80%+ while maintaining effectiveness.

---

## 🎯 Model Selection (Three-Tier Strategy)

### Haiku (Validation) - $0.25/$1.25 per M tokens
**Cheapest - use for simple checks:**
- Validating code syntax
- Checking file existence
- Simple status checks
- Quick confirmations
- Routine monitoring

### Sonnet (Content Creation) - $3/$15 per M tokens
**Default for most work:**
- Writing code
- Creating content
- Normal chat/coordination
- File operations
- Building features

### Opus (Reasoning) - $15/$75 per M tokens
**Spawn sub-agent for complex reasoning:**
- Deep debugging
- Architecture/design decisions
- Stuck after 2-3 attempts
- Multi-step problem solving
- Complex logic

**Example usage:**
```javascript
// Validation - spawn Haiku
sessions_spawn({
  task: "Check if all API endpoints return 200",
  model: "anthropic/claude-haiku-4",
  cleanup: "delete"
})

// Content - use Sonnet (current session)
// (already default)

// Reasoning - spawn Opus
sessions_spawn({
  task: "Debug why Vercel env vars aren't in client bundle",
  model: "anthropic/claude-opus-4", 
  thinking: "extended",
  cleanup: "delete"
})
```

---

## 🔥 Top Token Burners (Fix These)

### 1. Browser Automation
**Problem:** Vercel page snapshots = 3-5k tokens EACH
**Fix:**
- Use compact mode: `snapshot({compact: true})`
- Navigate directly, don't browse around
- Use curl for API checks instead of browser when possible
- Limit snapshots to max 3 per task

### 2. File Reading
**Problem:** Reading same files repeatedly
**Fix:**
- Remember what I just read (don't re-read)
- Use `memory_search` before loading full files
- Use `offset` and `limit` for large files
- Cache file contents mentally for the session

### 3. Long Build Logs
**Problem:** Vercel/build logs are huge
**Fix:**
- Don't read full logs unless necessary
- Search for specific errors
- Use `compact` mode for snapshots

### 4. Verbose Responses
**Problem:** Over-explaining every step
**Fix:**
- Be concise unless teaching
- Skip obvious narration ("Now I'll...")
- Just do the work, report results

### 5. Trial-and-Error
**Problem:** Trying multiple solutions without thinking
**Fix:**
- Think first, act once
- When stuck, spawn Opus sub-agent instead of guessing
- Check docs/examples before experimenting

---

## 📏 Hard Limits

### Per-Task Budgets:
- Validation/checking: <500 tokens (Haiku sub-agent)
- Simple query: <1k tokens (Sonnet)
- File operation: <2k tokens (Sonnet)
- Content creation: <5k tokens (Sonnet)
- Browser task: <10k tokens (Sonnet)
- Complex debugging: Spawn Opus sub-agent

### Red Flags (Stop & Reassess):
- Same file read 3+ times
- Same browser snapshot 3+ times
- More than 5 failed attempts → spawn Opus sub-agent
- Context over 150k → time to wrap up or spawn sub-agent

---

## 🎛️ Operational Rules

### Always Do:
✅ Use `compact: true` for browser snapshots
✅ Remember what I already know
✅ Spawn Haiku for validation tasks
✅ Spawn Opus for complex reasoning
✅ Default to Sonnet for content creation
✅ Be surgical with tool calls

### Never Do:
❌ Re-read files unnecessarily
❌ Take multiple snapshots of same page
❌ Over-explain simple operations
❌ Trial-and-error debugging in main session
❌ Load large files without `limit`

---

## 📊 Audit Checklist (Weekly)

- [ ] Check session_status for average token use
- [ ] Review memory files for bloat
- [ ] Verify heartbeat checks are minimal
- [ ] Confirm sub-agents are being used for heavy lifting
- [ ] Update this doc with new learnings

---

## 💡 Tonight's Lessons

**What burned tokens:**
1. Multiple Vercel page snapshots (10+ snapshots @ 3-5k each = 40k tokens)
2. Repeated file reads (chat page code read 3+ times)
3. Long trial-and-error loop (should've spawned Opus sub-agent)
4. Not using compact mode

**What to do differently:**
- Validation tasks → spawn Haiku sub-agent (cheapest)
- Content creation → use Sonnet (current session)
- Complex reasoning → spawn Opus sub-agent
- Browser snapshots: compact mode only, max 3 per task
- Remember what I read, don't re-read
- Think → plan → execute (not guess → try → retry)

---

**Last Updated:** 2026-02-02
**Next Review:** Weekly, or after any 50k+ token session
