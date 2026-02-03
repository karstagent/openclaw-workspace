# Advanced Token Optimization Strategies for AI Agents
*Research compiled: 2026-02-02*
*Target: <$200/month operational cost*

## Executive Summary

Token costs can be reduced by 70-90% through strategic optimization without sacrificing capability. This document covers advanced techniques beyond basic model selection: prompt caching, context management, sub-agent orchestration, smart compaction, and budget tracking systems.

---

## 1. Prompt Caching Strategies

### 1.1 How Prompt Caching Works

**OpenAI Automatic Caching:**
- Enabled automatically for prompts ≥1024 tokens
- 80% latency reduction, up to 90% cost reduction on cached tokens
- Cache hit requires exact prefix match
- In-memory retention: 5-10 minutes (up to 1 hour)
- Extended retention (24h): Available on GPT-5+ models

**Anthropic Prompt Caching:**
- Manual cache breakpoints (more control)
- Cache TTL: 5 minutes
- Charged at reduced rate for cache reads (~10% of write cost)
- Supports caching system prompts, tools, long documents

### 1.2 Optimization Techniques

**Structure for Maximum Cache Hits:**
```
[Static Content - CACHE THIS]
├── System prompt
├── Tool definitions
├── Long-term context (SOUL.md, AGENTS.md, etc.)
├── Project documentation
└── Example interactions

[Dynamic Content - END OF PROMPT]
├── Recent conversation history (last 5-10 turns)
├── Current user message
└── Session-specific variables
```

**Key Rules:**
1. **Front-load static content** - Place unchanging content at the beginning
2. **Exact prefix matching** - Any change in cached portion breaks the cache
3. **Minimum 1024 tokens** - Below this, caching doesn't activate
4. **Consistent formatting** - Even whitespace changes break cache hits
5. **Use cache keys** - Group similar requests with `prompt_cache_key` parameter

**Cost Calculation Example:**
```
Without caching:
- 10,000 input tokens × $3/M = $0.03 per request
- 100 requests/day = $3/day = $90/month

With 80% cache hit rate:
- 2,000 fresh tokens × $3/M = $0.006
- 8,000 cached tokens × $0.30/M = $0.0024
- Total: $0.0084 per request
- 100 requests/day = $0.84/day = $25/month
- Savings: $65/month (72% reduction)
```

---

## 2. Context Management Architecture

### 2.1 Tiered Memory System

**Immediate Context (Always Loaded):**
- Current session messages (last 10-20 turns)
- Active task context
- Critical system instructions
- ~5-15K tokens

**Session Context (Loaded on Demand):**
- Today's memory file
- Yesterday's memory file
- Relevant project files
- ~10-30K tokens

**Long-Term Memory (Loaded Selectively):**
- MEMORY.md (main session only)
- Historical daily logs (search → retrieve)
- Project archives
- ~5-50K tokens when needed

**Cold Storage (Never Directly Loaded):**
- Old conversation logs
- Archived projects
- Retrieved via semantic search or explicit query

### 2.2 Smart Context Loading Patterns

**Lazy Loading:**
```javascript
// Don't load everything upfront
// Load on first mention or explicit need

if (userMentions("GlassWall project")) {
  loadFile("projects/glasswall/README.md");
}

if (isMainSession && isFirstMessage) {
  loadFile("MEMORY.md");
} else {
  // Skip in subagents and group chats
}
```

**Context Pruning Rules:**
1. **Recency bias** - Keep last 10 messages, summarize older
2. **Relevance filtering** - Drop off-topic conversation branches
3. **Deduplication** - Don't repeat information already in system prompt
4. **Compression** - Summarize long tool outputs before storing

**Sliding Window with Summaries:**
```
[System Prompt - Cached]
[Summary of messages 1-50]     ← Compressed to 500 tokens
[Full messages 51-60]          ← 5,000 tokens
[Current user message]         ← 100 tokens
```

### 2.3 File Context Optimization

**Don't load redundant context:**
- ❌ Loading entire codebase into every request
- ❌ Re-reading unchanged documentation
- ✅ Load only relevant files based on task
- ✅ Use file summaries/indexes for discovery

**Smart File Loading:**
```bash
# Bad: Load everything
cat $(find . -name "*.md")

# Good: Load what's needed
# 1. Check if file is already in context
# 2. Load only if mentioned or required for task
# 3. Use file excerpts, not full content
```

---

## 3. Sub-Agent Orchestration Patterns

### 3.1 When to Spawn Sub-Agents

**Cost-Effective Scenarios:**
1. **Model tier switching** - Use Haiku for validation, Opus for complex reasoning
2. **Parallel work** - Multiple independent tasks
3. **Context isolation** - Prevent context pollution
4. **Long-running tasks** - Offload from main session
5. **Budget quarantine** - Limit expensive operations

**Anti-Patterns (Wasteful):**
- ❌ Spawning sub-agent for simple tasks main agent can handle
- ❌ Passing huge context to sub-agent (defeats isolation purpose)
- ❌ Creating sub-agent chains (exponential overhead)
- ❌ Using Opus sub-agent when Sonnet would suffice

### 3.2 Three-Tier Model Strategy

**Tier 1: Haiku (Validation/Checking)**
- Cost: ~$0.25/M input, ~$1.25/M output
- Use for: Syntax checking, format validation, simple parsing
- Spawn as sub-agent for quick checks
- Expected token usage: 1K-5K per task

**Tier 2: Sonnet (Default/Creation)**
- Cost: ~$3/M input, ~$15/M output
- Use for: Content creation, normal interactions, code generation
- Main session default
- Expected token usage: 5K-50K per task

**Tier 3: Opus (Complex Reasoning)**
- Cost: ~$15/M input, ~$75/M output
- Use for: Complex debugging, architectural decisions, stuck problems
- Spawn as sub-agent only when needed
- Expected token usage: 10K-100K per task

**Decision Matrix:**
```
Simple validation → Haiku sub-agent
Normal task → Sonnet (current session)
Stuck/complex → Opus sub-agent (with detailed context)
```

### 3.3 Sub-Agent Communication Efficiency

**Minimize context transfer:**
```
# Bad: Pass entire conversation history
spawn_subagent(context=full_history) # 50K tokens

# Good: Pass only what's needed
spawn_subagent(context={
  task: "Validate JSON schema",
  data: schema_file,
  rules: validation_rules
}) # 2K tokens
```

**Task-Specific Prompts:**
```
# Generic (wasteful):
"You are a helpful assistant. Help with this task: [...]"

# Specific (efficient):
"Validate this JSON schema. Reply VALID or ERROR: [details]."
```

---

## 4. Smart Context Compaction

### 4.1 Conversation Summarization

**Rolling Summary Pattern:**
```
Every 20 messages:
1. Summarize messages 1-20 into 200-500 tokens
2. Keep full messages 21-40
3. Append new messages

Result: Maintain coherence while limiting growth
```

**Summary Quality Tiers:**
- **High-fidelity** (1:5 ratio) - Important decisions, complex discussions
- **Standard** (1:10 ratio) - Normal conversation flow
- **Minimal** (1:20 ratio) - Small talk, confirmations

**What to Preserve in Summaries:**
- Decisions made
- Key facts learned
- Tasks assigned
- Important context changes
- User preferences expressed

**What to Drop:**
- Pleasantries ("thanks", "sounds good")
- Redundant confirmations
- Temporary troubleshooting steps
- Repeated information

### 4.2 Tool Output Compaction

**Large Tool Outputs:**
```python
# Bad: Include full output in context
result = exec("find . -name '*.js'")  # 5000 lines
context.append(result)  # 50K tokens!

# Good: Summarize or truncate
result = exec("find . -name '*.js'")
summary = f"Found {len(result.split('\n'))} JavaScript files"
context.append(summary)  # 50 tokens
```

**Structured Data Handling:**
- JSON responses: Extract only relevant fields
- Log files: Show summary + last 50 lines
- Directory listings: Count + sample entries
- Search results: Top 10 + total count

### 4.3 Code Context Optimization

**Function-Level Context:**
```
# Instead of full file (500 lines, 5K tokens):
def process_data(input):
    # ... 500 lines

# Include only signature + docstring (50 tokens):
"""
def process_data(input: dict) -> dict:
    Process user data and return normalized format.
"""
```

**Smart Code Extraction:**
1. Load full file only when editing
2. For references, load signature + docstring
3. Use code maps/indexes for discovery
4. Inline only the specific function being modified

---

## 5. Budget Tracking & Governance

### 5.1 Token Budget System

**Per-Session Budgets:**
```json
{
  "budgets": {
    "main_session": {
      "daily": 500000,
      "per_request": 50000,
      "emergency_reserve": 100000
    },
    "subagent_haiku": {
      "per_task": 10000
    },
    "subagent_opus": {
      "per_task": 100000,
      "requires_justification": true
    }
  }
}
```

**Budget Tracking Implementation:**
```javascript
class TokenBudget {
  constructor(dailyLimit) {
    this.dailyLimit = dailyLimit;
    this.usedToday = 0;
    this.resetDate = new Date().toDateString();
  }
  
  checkAndReserve(estimatedTokens) {
    this.resetIfNewDay();
    
    if (this.usedToday + estimatedTokens > this.dailyLimit) {
      throw new Error(`Budget exceeded: ${this.usedToday}/${this.dailyLimit}`);
    }
    
    this.usedToday += estimatedTokens;
    return true;
  }
  
  getRemaining() {
    return this.dailyLimit - this.usedToday;
  }
}
```

### 5.2 Cost Monitoring

**Track by Category:**
```json
{
  "daily_usage": {
    "2026-02-02": {
      "main_session": {
        "requests": 45,
        "input_tokens": 234000,
        "output_tokens": 67000,
        "cached_tokens": 180000,
        "cost": 2.34
      },
      "subagent_haiku": {
        "requests": 12,
        "cost": 0.08
      },
      "subagent_opus": {
        "requests": 2,
        "cost": 1.85
      },
      "total_cost": 4.27
    }
  }
}
```

**Monthly Budget Allocation ($200 target):**
```
Main sessions (Sonnet):        $120 (60%)
Sub-agents (Haiku):            $20  (10%)
Sub-agents (Opus):             $40  (20%)
Reserve/overflow:              $20  (10%)
-------------------------------------------
Total:                         $200/month
```

**Alert Thresholds:**
- 50% of daily budget → Warning
- 75% of daily budget → Review required
- 90% of daily budget → Throttle non-essential requests
- 100% of daily budget → Emergency mode (Haiku only)

### 5.3 Cost Optimization Triggers

**Automatic Throttling:**
```
If daily_cost > daily_budget * 0.75:
  - Switch to Haiku for non-critical tasks
  - Increase summarization ratio (1:10 → 1:20)
  - Defer non-urgent background tasks
  - Reduce heartbeat frequency

If daily_cost > daily_budget * 0.90:
  - Emergency mode: essential operations only
  - Skip all heartbeat checks
  - Minimal context loading
  - User notification required for Opus usage
```

---

## 6. Advanced Techniques

### 6.1 Semantic Deduplication

**Problem:** Same information appears multiple times in context
**Solution:** Hash-based deduplication

```python
from hashlib import md5

seen_content = set()

def add_to_context(content):
    content_hash = md5(content.encode()).hexdigest()
    
    if content_hash in seen_content:
        return  # Skip duplicate
    
    seen_content.add(content_hash)
    context.append(content)
```

### 6.2 Differential Context Updates

**Instead of reloading everything:**
```
Session 1: Load AGENTS.md (5K tokens)
Session 2: AGENTS.md unchanged → Use cached version
Session 3: AGENTS.md modified → Load only diff
```

**Git-style diffs for context:**
```diff
# Only send changes, not full file
@@ -45,3 +45,5 @@
 ## Memory
 
 You wake up fresh each session.
+
+**New rule:** Always check TOKEN_STRATEGY.md
```

### 6.3 Predictive Context Loading

**Learn access patterns:**
```javascript
const contextPatterns = {
  "email task": ["gmail_access.md", "email_templates.md"],
  "code task": ["coding_style.md", "project_structure.md"],
  "calendar task": ["calendar_access.md"]
};

function predictContext(userMessage) {
  const taskType = classifyTask(userMessage);
  return contextPatterns[taskType] || [];
}
```

### 6.4 Token Estimation Before Execution

**Pre-check expensive operations:**
```python
def estimate_tokens(text):
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) / 4

if estimate_tokens(large_file) > 50000:
    # Too large, use summary instead
    return summarize_file(large_file)
else:
    return large_file
```

### 6.5 Batch Operations

**Combine multiple small tasks:**
```
# Bad: 5 separate requests
validate_json(file1)  # 2K tokens
validate_json(file2)  # 2K tokens
validate_json(file3)  # 2K tokens
validate_json(file4)  # 2K tokens
validate_json(file5)  # 2K tokens
# Total: 10K tokens, overhead × 5

# Good: 1 batched request
validate_json([file1, file2, file3, file4, file5])
# Total: 6K tokens, overhead × 1
```

---

## 7. Practical Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Implement token budget tracking system
- [ ] Set up daily cost monitoring dashboard
- [ ] Restructure prompts for caching (static content first)
- [ ] Configure cache retention policies

**Expected savings:** 30-40%

### Phase 2: Context Optimization (Week 2)
- [ ] Implement tiered memory system
- [ ] Add conversation summarization (every 20 messages)
- [ ] Create context loading rules (lazy loading)
- [ ] Set up tool output compaction

**Expected savings:** 20-30%

### Phase 3: Sub-Agent Strategy (Week 3)
- [ ] Define Haiku/Sonnet/Opus decision matrix
- [ ] Create sub-agent task templates
- [ ] Implement budget-aware model selection
- [ ] Build sub-agent monitoring

**Expected savings:** 15-25%

### Phase 4: Advanced Optimizations (Week 4)
- [ ] Semantic deduplication system
- [ ] Predictive context loading
- [ ] Batch operation handlers
- [ ] Automated throttling triggers

**Expected savings:** 10-15%

**Cumulative potential savings: 75-85%**

---

## 8. Real-World Cost Scenarios

### Scenario A: Email Management Agent
**Without optimization:**
- 100 email checks/day × 15K tokens/check = 1.5M tokens/day
- Cost: ~$4.50/day = $135/month

**With optimization:**
- Static prompt (10K tokens, 80% cached) → 2K fresh per request
- Batch checks (5 emails/request) → 20 requests/day
- Summary mode for old emails → 5K tokens/request average
- Cost: 20 × 5K × $0.003 = $0.30/day = $9/month
- **Savings: $126/month (93%)**

### Scenario B: Code Review Agent
**Without optimization:**
- 20 code reviews/day × 40K tokens/review = 800K tokens/day
- Cost: ~$2.40/day = $72/month

**With optimization:**
- Function-level context (not full files) → 15K tokens/review
- Haiku for syntax validation → $0.25/M vs $3/M
- Cached project structure → 70% cache hit rate
- Cost: 20 × 15K × 0.3 × $0.003 = $0.27/day = $8/month
- **Savings: $64/month (89%)**

### Scenario C: Multi-Purpose Personal Agent
**Target: <$200/month**

**Budget allocation:**
```
Heartbeat checks (4×/day):        $15/month
Email management (1×/day):        $20/month
Calendar/scheduling:              $15/month
Code assistance (ad-hoc):         $40/month
Research tasks (Opus, 3×/week):   $50/month
General conversation:             $40/month
Reserve:                          $20/month
-------------------------------------------
Total:                            $200/month
```

**Optimization strategies applied:**
- Heartbeat: Batch checks, use Haiku, smart scheduling
- Email: Summary mode, caching, batch processing
- Calendar: Cached context, minimal refreshes
- Code: Context isolation, function-level loading
- Research: Spawn Opus sub-agents only when justified
- Conversation: Aggressive summarization, cache system prompts

---

## 9. Monitoring & Metrics

### Key Metrics to Track

**Daily:**
- Total tokens used (input/output/cached)
- Cost per category
- Cache hit rate
- Average tokens per request
- Budget utilization %

**Weekly:**
- Cost trend (increasing/decreasing)
- Optimization effectiveness
- Sub-agent usage patterns
- Context size trends

**Monthly:**
- Total cost vs. budget
- ROI on optimization efforts
- Model tier distribution
- Bottleneck identification

### Dashboard Template

```
╔══════════════════════════════════════════════════════╗
║  Token Budget Dashboard - 2026-02-02                 ║
╠══════════════════════════════════════════════════════╣
║  Daily Budget:        50,000 tokens                  ║
║  Used Today:          34,567 tokens (69%)            ║
║  Remaining:           15,433 tokens (31%)            ║
║                                                      ║
║  Cache Hit Rate:      78%                            ║
║  Avg Request Size:    8,500 tokens                   ║
║                                                      ║
║  Estimated Daily Cost: $3.21                         ║
║  Monthly Projection:   $96.30                        ║
║                                                      ║
║  Status: ✅ Within budget                            ║
╚══════════════════════════════════════════════════════╝
```

---

## 10. Best Practices Checklist

### Before Every Request
- [ ] Is this prompt cacheable? (Static content first?)
- [ ] Can I use cached context from previous request?
- [ ] Is Haiku sufficient, or do I need Sonnet/Opus?
- [ ] Can I batch this with other pending tasks?
- [ ] Do I really need all this context?

### Context Management
- [ ] Load files lazily (on demand, not upfront)
- [ ] Summarize conversations every 20 messages
- [ ] Compress large tool outputs
- [ ] Remove redundant/outdated information
- [ ] Use references instead of inline content when possible

### Sub-Agent Usage
- [ ] Is this complex enough to warrant sub-agent?
- [ ] Am I passing minimal context to sub-agent?
- [ ] Is this the right model tier for the task?
- [ ] Have I justified Opus usage if applicable?

### Budget Discipline
- [ ] Check remaining budget before expensive operations
- [ ] Log token usage for all requests
- [ ] Review daily spend each evening
- [ ] Throttle when approaching limits
- [ ] Reserve budget for emergencies

---

## 11. Common Pitfalls & Solutions

### Pitfall 1: "Cache Invalidation Cascade"
**Problem:** Small change in system prompt invalidates entire cache
**Solution:** Move volatile content to end of prompt, keep system prompt stable

### Pitfall 2: "Context Hoarding"
**Problem:** Loading everything "just in case"
**Solution:** Implement lazy loading, load on first mention

### Pitfall 3: "Sub-Agent Sprawl"
**Problem:** Creating too many sub-agents for trivial tasks
**Solution:** Use decision matrix, minimum complexity threshold

### Pitfall 4: "Summary Drift"
**Problem:** Repeated summarization loses critical details
**Solution:** High-fidelity summaries for important conversations, preserve key decisions verbatim

### Pitfall 5: "Budget Blindness"
**Problem:** Not tracking costs until month-end surprise
**Solution:** Daily monitoring, automated alerts at 50%/75%/90% thresholds

---

## 12. Future Optimizations to Watch

### Emerging Techniques
- **Semantic caching** - Cache by meaning, not exact match
- **Compressed KV cache** - Reduced memory footprint for cached prompts
- **Multi-tenant caching** - Shared caches across similar agents (privacy-safe)
- **Learned context prioritization** - ML-based relevance scoring
- **Streaming summarization** - Real-time conversation compression

### Provider Roadmaps
- OpenAI: Extended cache retention for all models
- Anthropic: Automatic cache breakpoint detection
- Google: Gemini context caching improvements
- Open-source: Local caching layers for self-hosted models

---

## 13. Conclusion

**Token optimization is not about restriction—it's about efficiency.**

By implementing these strategies, a personal AI agent can operate at <$200/month while maintaining high capability:

1. **70-85% cost reduction** through prompt caching alone
2. **Additional 10-20%** through smart context management
3. **Another 10-15%** through strategic sub-agent orchestration
4. **Final 5-10%** through budget discipline and monitoring

**The key insight:** Most tokens are wasted on redundant context, poor prompt structure, and inappropriate model selection. Fix those, and costs plummet.

**Start small, measure everything, iterate constantly.**

---

## References & Further Reading

### Documentation
- [OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching)
- [Anthropic Prompt Caching](https://docs.anthropic.com/claude/docs/prompt-caching)
- [Token Usage Best Practices](https://platform.openai.com/docs/guides/optimizing)

### Tools
- Token counters: tiktoken (OpenAI), anthropic-tokenizer
- Budget tracking: Custom implementation recommended
- Context management: LangChain, LlamaIndex (adapt patterns)

### Community Resources
- AI agent optimization communities
- Cost tracking spreadsheets
- Open-source budget management tools

---

*Last updated: 2026-02-02*
*Target cost: <$200/month*
*Maintainer: Personal AI Agent*
