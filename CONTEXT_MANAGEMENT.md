# Context Management Guide

## Understanding the Context Limit

Claude has a 200K token context limit, which includes both input tokens (history + current message) and the tokens reserved for the response. When we hit this limit, the LLM can't process the request.

## Our Solution

We've implemented a three-layer approach to prevent context overflows:

### 1. Automatic Context Pruning

- **Mode**: cache-ttl
- **Time-To-Live**: 3 hours
- **Soft Trimming**: When context reaches 70% capacity, older context is summarized
- **Hard Clearing**: When context reaches 90% capacity, older context is removed entirely
- **Preservation**: Always keeps the last assistant message

### 2. Session Reset Policies

- **Idle Reset**: Sessions automatically reset after 24 hours of inactivity
- **Manual Reset**: Use `/new` command to manually reset context when needed

### 3. Daily Cron Job

- Scheduled at 4:00 AM PST
- Sends a reminder to reset context if necessary

## Best Practices

1. **Start Fresh When Changing Topics**: Use `/new` when switching to a completely different conversation topic
2. **Regular Maintenance**: During heartbeat checks, evaluate if context reset is needed
3. **Summarize Important Information**: Before resetting, capture important context in `MEMORY.md`

## Memory vs. Context

- **Context**: Short-term, in-session knowledge (cleared on reset)
- **Memory**: Long-term knowledge stored in `MEMORY.md` and searchable via vector recall

Remember: Memory persists across sessions, context doesn't.