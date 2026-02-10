# Model Selection Strategy

This file provides guidelines for intelligent model selection based on task type and complexity.

## Model Tiers

### Haiku (Claude 3.5 Haiku)
- **Use for**: Routine tasks, information retrieval, status checks, summaries
- **Strengths**: Fast, cost-effective, good for regular background processes
- **Drawbacks**: Limited reasoning, less nuanced responses
- **Best fit for**:
  - Heartbeat checks
  - Status monitoring
  - Data retrieval
  - Simple administrative tasks

### Sonnet (Claude 3.7 Sonnet)
- **Use for**: Strategic thinking, complex analysis, important communications
- **Strengths**: Strong reasoning, nuanced understanding, handles complexity well
- **Drawbacks**: More expensive, slightly slower than Haiku
- **Best fit for**:
  - Research projects
  - Strategic planning
  - Complex content creation
  - Important decision-making

### DeepSeek (DeepSeek Coder)
- **Use for**: Code analysis, development tasks, technical documentation
- **Strengths**: Specialized for code, technical understanding
- **Drawbacks**: Less suited for general tasks, creative content
- **Best fit for**:
  - Code development
  - Debugging
  - Technical analysis
  - API integration

## Task-Based Selection Guidelines

### Background Processes
- **Default model**: Haiku
- **Thinking level**: Low or minimal
- **Example tasks**: Heartbeat checks, API monitoring, routine status updates
- **Rationale**: These frequent, lightweight tasks don't require deep reasoning

### Development Work
- **Default model**: DeepSeek or Sonnet (depending on complexity)
- **Thinking level**: Medium or high
- **Example tasks**: GlassWall development, debugging, API integration
- **Rationale**: Technical tasks benefit from specialized models or stronger reasoning

### Strategic Analysis
- **Default model**: Sonnet
- **Thinking level**: High
- **Example tasks**: Project planning, research analysis, business strategy
- **Rationale**: Complex tasks benefit from stronger reasoning capabilities

### Communication
- **Default model**: Sonnet for important communications, Haiku for routine updates
- **Thinking level**: Varies based on importance
- **Example tasks**: Progress reports, strategic summaries, feedback analysis
- **Rationale**: Important communications require nuance and depth

## OpenClaw Configuration

This strategy can be implemented in OpenClaw through:

1. **Default model configuration**:
```
openclaw configure agents.defaults.models.default sonnet
openclaw configure agents.defaults.models.admin haiku
openclaw configure agents.defaults.models.background haiku
```

2. **Cron job model selection**:
```
openclaw cron add \
  --name "Strategic Analysis" \
  --cron "0 9 * * 1" \
  --session isolated \
  --message "..." \
  --model "sonnet" \
  --thinking high
```

3. **Heartbeat checks**:
Each heartbeat check in the rotating system has its own recommended model.

4. **Dynamic model switching**:
For complex workflows, start with Haiku for initial data gathering, then switch to Sonnet for analysis when needed.

## Token Efficiency Guidelines

- Use HEARTBEAT_OK for routine checks with no issues
- Keep prompt contexts small for background tasks
- Organize files to minimize context bloat
- Use isolated cron jobs for heavy processing
- Consider lower thinking levels for routine tasks

## Implementation Notes

This strategy is implemented in:
- `/Users/karst/.openclaw/workspace/autonomous/heartbeat_runner.py`
- `/Users/karst/.openclaw/workspace/autonomous/cron_job_manager.py`

Adjust model selection as needed based on task performance and cost considerations.