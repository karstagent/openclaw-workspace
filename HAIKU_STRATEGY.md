# Haiku Cost Optimization Strategy

## Goal
Reduce costs by 70-80% while maintaining build quality

## Rules

### ALWAYS use Haiku for:
1. **Heartbeat monitoring** - checking email/calendar/system
2. **Status checks** - Vercel, database, API health
3. **Data fetching** - API calls, parsing responses
4. **File operations** - reading logs, moving files, cleanup
5. **Progress tracking** - updating roadmap checkboxes, memory files
6. **Simple updates** - git commits, timestamp updates
7. **Verification** - test if deploy worked, API returns 200
8. **Brief communication** - "Done" messages, HEARTBEAT_OK

### ALWAYS use Sonnet for:
1. **Building features** - new API endpoints, components
2. **Complex edits** - multi-file changes, refactors
3. **Architecture decisions** - design choices, patterns
4. **Debugging** - tracing subtle bugs, fix complex issues
5. **Product strategy** - roadmap decisions, feature planning
6. **React/TypeScript** - component logic, type definitions

## Implementation
- Spawn Haiku sub-agents for routine work: `sessions_spawn(task="...", model="haiku")`
- Use Sonnet (self) only for complex building
- Batch Haiku tasks together when possible

## Expected Savings
- Current: ~$5-10/day
- Target: ~$1-2/day (80% reduction)
- Heartbeats: $0.005 each (vs $0.02 Sonnet)
- Routine work: 90% cheaper
- Building: Same quality, same cost

## Quality Monitoring
Track if Haiku causes:
- More clarifying questions needed
- Lower quality simple edits
- Bugs introduced in routine updates
- Adjust strategy if quality drops
