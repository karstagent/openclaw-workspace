# OPTIMIZATION.md - Token Optimization Guide

## Session Initialization Rule
On every session start:
1. Load ONLY these files:
   - SOUL.md
   - USER.md
   - IDENTITY.md
   - memory/YYYY-MM-DD.md (if it exists)
2. DO NOT auto-load:
   - MEMORY.md
   - Session history
   - Prior messages
   - Previous tool outputs
3. When user asks about prior context:
   - Use memory_search() on demand
   - Pull only the relevant snippet with memory_get()
   - Don't load the whole file
4. Update memory/YYYY-MM-DD.md at end of session with:
   - What you worked on
   - Decisions made
   - Leads generated
   - Blockers
   - Next steps

## Model Selection Rule
Default: Claude Haiku

Switch to Sonnet ONLY when:
- Architecture decisions
- Production code review
- Security analysis
- Complex debugging/reasoning
- Strategic multi-project decisions

When in doubt: Try Haiku first.

## Rate Limits
- 5 seconds minimum between API calls
- 10 seconds between web searches
- Max 5 searches per batch, then 2-minute break
- Batch similar work (one request for 10 leads, not 10 requests)
- If you hit 429 error: STOP, wait 5 minutes, retry

## Budgets
- DAILY BUDGET: $5 (warning at 75%)
- MONTHLY BUDGET: $200 (warning at 75%)

## Caching Strategy
- Keep static content in dedicated files for better caching
- Batch requests within 5-minute windows when possible
- Separate stable from dynamic content
- System prompts stay stable during sessions