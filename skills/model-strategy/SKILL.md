---
name: model-strategy
description: Manage model selection for cost optimization. Use when choosing between models (Haiku/Sonnet/Opus) for different tasks, spawning sub-agents, or optimizing token usage. Implements the three-tier strategy for validation, building, and complex reasoning.
---

# Model Strategy

Core principle: Use the right model for the job - no more, no less.

**Default routing: Always use OpenRouter** for consistent access and simplified configuration.

## Model Aliases & Costs

### OpenRouter Models (Default)
**Always use OpenRouter for sub-agents** - consistent routing, verified working.

OpenRouter automatically optimizes routing based on price and uptime. You can further optimize with shortcuts:

```javascript
// ✅ DeepSeek - Cheapest validation (with :floor for guaranteed lowest price)
sessions_spawn({ 
  model: "openrouter/deepseek/deepseek-chat:floor",
  task: "...",
  thinking: "off"
})

// ✅ Haiku - High-accuracy validation (with :nitro for speed)
sessions_spawn({ 
  model: "openrouter/anthropic/claude-3.5-haiku:nitro",
  task: "...",
  thinking: "off"
})

// ✅ Sonnet - Complex building tasks (with :floor for cost optimization)
sessions_spawn({ 
  model: "openrouter/anthropic/claude-3.5-sonnet:floor",
  task: "..."
})
```

**OpenRouter Shortcuts:**
- `:floor` - Always routes to cheapest provider (price-optimized)
- `:nitro` - Always routes to fastest provider (throughput-optimized)

### Available Models
| Model | Path | Cost/1M | Use For |
|-------|------|---------|---------|
| DeepSeek | openrouter/deepseek/deepseek-chat | $0.14 | Validation, extraction, parsing |
| Gemini | openrouter/google/gemini-2.0-flash-exp:free | $0.10 | Alternative cheap validation |
| Haiku | openrouter/anthropic/claude-3.5-haiku | $0.25 | High-accuracy validation |
| Sonnet | openrouter/anthropic/claude-3.5-sonnet | $3 | Building, complex tasks |

**Note:** Main session uses direct Anthropic (anthropic/claude-sonnet-4-5) which works fine for the primary agent.

## OpenRouter Auto-Optimization

OpenRouter provides automatic optimization and smart routing features:

### Automatic Load Balancing (Default)
- Routes to lowest-cost providers automatically
- Considers uptime and reliability
- Uses inverse-square weighting (cheaper = more traffic)
- **No configuration needed** - works out of the box

### Optimization Shortcuts

**:floor** - Guaranteed lowest price
```javascript
model: "openrouter/deepseek/deepseek-chat:floor"
// Always routes to the cheapest provider
// Best for: Cost-sensitive validation tasks
```

**:nitro** - Maximum throughput
```javascript
model: "openrouter/anthropic/claude-3.5-haiku:nitro"
// Always routes to the fastest provider
// Best for: Time-sensitive operations
```

### Advanced Provider Configuration

For fine-grained control, use provider settings:

```javascript
sessions_spawn({
  model: "openrouter/deepseek/deepseek-chat",
  task: "...",
  // Advanced options (rarely needed):
  // provider: {
  //   sort: "price",  // or "throughput" or "latency"
  //   preferredMinThroughput: { p90: 50 },  // tokens/sec
  //   preferredMaxLatency: { p90: 3 }       // seconds
  // }
})
```

### Recommended Defaults

For most use cases, use these patterns:

**Cost-optimized (validation):**
```javascript
model: "openrouter/deepseek/deepseek-chat:floor"
```

**Speed-optimized (time-sensitive):**
```javascript
model: "openrouter/anthropic/claude-3.5-haiku:nitro"
```

**Balanced (default):**
```javascript
model: "openrouter/anthropic/claude-3.5-sonnet"
// OpenRouter auto-balances price and uptime
```

DeepSeek and Gemini are excellent cost-effective alternatives for validation and routine tasks, being even cheaper than Haiku.

## Three-Tier Strategy (OpenRouter Default)

1. **DeepSeek/Haiku** (~$0.14-0.25/1M tokens) via OpenRouter
   - Validation/checking
   - Data extraction
   - Format verification
   - Simple yes/no decisions
   - ALWAYS spawn sub-agents with `openrouter/deepseek/deepseek-chat` or `openrouter/anthropic/claude-3.5-haiku`

2. **Sonnet** (~$3/1M tokens)
   - Main session: `anthropic/claude-sonnet-4-5` (direct)
   - Sub-agents: `openrouter/anthropic/claude-3.5-sonnet`
   - Content creation, code writing, normal interactions, most building tasks

3. **Opus** (~$15/1M tokens)
   - Complex reasoning, stuck problems, architecture decisions
   - Use sparingly via sub-agents when Sonnet isn't enough
   - Try Sonnet first, escalate to Opus only if needed

## When to Use Each Model

### Haiku/DeepSeek Tier ($0.14-0.25/1M)
Best for:
- Format validation (JSON, email, URLs)
- Data extraction & parsing
- Simple transformations
- Pattern matching
- Quick yes/no decisions
- Monitoring tasks

Choose DeepSeek when cost is priority ($0.14/1M) or Haiku when highest accuracy needed ($0.25/1M).

Example spawns:
```javascript
// Cost-optimized with DeepSeek (cheapest, :floor ensures lowest price)
sessions_spawn({
  model: "openrouter/deepseek/deepseek-chat:floor",
  task: "Extract all email addresses from this text",
  thinking: "off"
})

// High-accuracy with Haiku (:nitro for speed when accuracy needed)
sessions_spawn({
  model: "openrouter/anthropic/claude-3.5-haiku:nitro",
  task: "Extract all email addresses from this text",
  thinking: "off"
})
```

### Sonnet ($3/1M)
Best for:
- Normal conversations
- Content writing
- Code development
- Feature building
- Most daily tasks

This is your default model - no special configuration needed.

### Opus ($15/1M)
Best for:
- Complex debugging
- System architecture
- Stuck problems
- Deep reasoning tasks

Example spawn:
```javascript
sessions_spawn({
  model: "sonnet",  // Try Sonnet first
  task: "Debug this complex race condition...",
  thinking: "on"    // Enable reasoning for hard problems
})

// If still stuck after Sonnet attempt:
sessions_spawn({
  model: "opus",
  task: "Previous attempt with Sonnet failed. Debug race condition...",
  thinking: "on"
})
```

## Cost Optimization

### Token Saving Patterns

1. **Validation First**
   ```javascript
   // Bad: Validate in main session
   if (isValidJson(data)) { ... }

   // Good: Spawn DeepSeek sub-agent (:floor for guaranteed lowest cost)
   sessions_spawn({
     model: "openrouter/deepseek/deepseek-chat:floor",
     task: "Is this valid JSON? Reply only YES/NO: " + data,
     thinking: "off"
   })
   ```

2. **Batch Similar Tasks**
   ```javascript
   // Bad: Multiple spawns
   sessions_spawn({ 
     model: "openrouter/deepseek/deepseek-chat:floor", 
     task: "Check email 1" 
   })
   sessions_spawn({ 
     model: "openrouter/deepseek/deepseek-chat:floor", 
     task: "Check email 2" 
   })

   // Good: Single spawn with batch
   sessions_spawn({
     model: "openrouter/deepseek/deepseek-chat:floor",
     task: "Check these emails:\n1. ...\n2. ...",
     thinking: "off"
   })
   ```

3. **Progressive Enhancement**
   Start with Sonnet, only escalate to Opus if needed:
   ```javascript
   // First attempt with Sonnet
   sessions_spawn({
     model: "sonnet",
     task: "Design the database schema..."
   })

   // Only if stuck, try Opus
   sessions_spawn({
     model: "opus",
     task: "Previous Sonnet attempt failed. Schema requirements..."
   })
   ```

### Cost Tracking

Track model usage in your daily memory files:
```markdown
## Model Usage (2026-02-03)
- Haiku: 15 validations (~$0.05)
- Sonnet: Normal building (~$0.75)
- Opus: 1 architecture review (~$0.30)
Total: ~$1.10
```

## Best Practices

1. **Always validate with DeepSeek/Haiku via OpenRouter**
   - Never use main session for simple checks
   - Spawn OpenRouter sub-agents for all validation
   - Default to DeepSeek for cost, Haiku for accuracy

2. **Think before upgrading**
   - Try Sonnet first for hard problems
   - Only escalate to Opus if truly stuck
   - Document why you needed Opus

3. **Batch similar tasks**
   - Combine related validations
   - Group similar checks together
   - Minimize spawns when possible

4. **Monitor and optimize**
   - Track daily model usage
   - Look for patterns to optimize
   - Document expensive operations

5. **Zero tolerance for failures**
   - If ANY model call fails, stop and fix it immediately
   - Document the error and solution in daily memory
   - Update relevant skills/tools to prevent recurrence
   - Test the fix thoroughly before continuing
   - Example fixes:
     - Check model availability/naming
     - Verify API access and rate limits
     - Update model aliases if deprecated
     - Add error handling patterns that worked

## Quick Reference (OpenRouter-First)

| Task Type | Model Path | Cost/1M | When to Use |
|-----------|------------|---------|-------------|
| Validation (cost) | openrouter/deepseek/deepseek-chat:floor | $0.14 | Default for checks, parsing, extraction |
| Validation (speed) | openrouter/anthropic/claude-3.5-haiku:nitro | $0.25 | High-accuracy validation with speed |
| Building | openrouter/anthropic/claude-3.5-sonnet:floor | $3 | Sub-agent building tasks (cost-optimized) |
| Building | anthropic/claude-sonnet-4-5 | $3 | Main session (direct) |
| Complex | openrouter/anthropic/claude-3.5-opus | $15 | When Sonnet isn't enough |

**Default strategy:**
- All sub-agents → OpenRouter paths with `:floor` or `:nitro` shortcuts
- Main session → Direct Anthropic (works fine)
- Validation → DeepSeek `:floor` for cost, Haiku `:nitro` for speed
- Keep main context clean with sub-agents
- OpenRouter auto-optimizes routing (load balancing, uptime, fallbacks)

Remember: The goal is maximum value per token. Use the cheapest model that can reliably complete the task.