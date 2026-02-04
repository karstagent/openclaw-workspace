# MODEL_STRATEGY.md - Smart Cost Optimization

**Default:** DeepSeek ($0.14/1M input, $0.28/1M output)

## My Decision Rules

### I Run on DeepSeek For:
- ✅ Heartbeat checks (monitoring, status updates)
- ✅ Routine updates (email checks, calendar, notifications)
- ✅ Simple conversations
- ✅ File operations (read, write, search)
- ✅ Progress reporting
- ✅ Documentation updates
- ✅ Git operations

### I Spawn Sonnet Sub-Agents For:
- 🎯 Building new features (code generation, architecture)
- 🎯 Complex debugging (multi-step problem solving)
- 🎯 Critical decisions (product strategy, design choices)
- 🎯 Writing important content (marketing copy, user-facing docs)
- 🎯 Complex API integrations
- 🎯 Anything where quality/reasoning really matters

### I Use Gemini Flash (Free) For:
- 📝 Quick validation checks
- 📝 Testing (does this work?)
- 📝 Simple data transformations
- 📝 Batch operations that don't need precision

## Cost Impact

**Before (all Sonnet):**
- Heartbeats: $21/day
- Routine work: $8/day
- Conversations: $6/day
- Building: $25/day
- **Total: $60/day**

**After (smart defaults):**
- Heartbeats: $0.20/day (DeepSeek)
- Routine work: $0.10/day (DeepSeek)
- Conversations: $0.15/day (DeepSeek)
- Building: $25/day (Sonnet sub-agents)
- **Total: ~$27/day**

**Savings: $33/day = $12,000/year**

## Override Anytime

You can always force a model:
- `/model sonnet` - Switch me to Sonnet directly
- `/model gemini` - Switch me to free tier
- `/model deepseek` - Back to default

---

**Philosophy:** Optimize for cost on routine work, splurge on quality when it matters. I'll make the judgment calls.
