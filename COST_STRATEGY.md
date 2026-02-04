# Cost Reduction Strategy

## Current Measures (Active)
1. ✅ Heartbeat: 10 minutes (was 5min)
2. ✅ Context trimmed: .clawignore excludes large docs
3. ✅ Haiku for simple tasks (quality-preserving)
4. ✅ Batched work (longer responses, fewer turns)

## Model Selection Rules
- **Haiku** for: Simple edits, monitoring, quick checks
- **Sonnet** for: Building features, complex logic, writing
- **Opus** for: Never (too expensive, no need)
- **Coding agents** for: Major refactors only

## Heartbeat Efficiency
- 10min interval = 6/hour
- ~$0.02/heartbeat = $0.12/hour
- Daily: ~$3 in heartbeats (manageable)

## Turn Reduction
- Batch multiple changes in one response
- Longer, complete answers vs back-and-forth
- Use coding agents for multi-file work

## Target Costs
- Daily budget: ~$5-10 (sustainable)
- Current burn rate: ~$2-3/day (after fixes)
