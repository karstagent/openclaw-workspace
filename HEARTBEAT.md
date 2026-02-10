# Intelligent Heartbeat System

The OpenClaw agent uses a rotating priority-based heartbeat system to efficiently manage automated tasks without overwhelming resources or creating redundant checks.

## Heartbeat Execution Flow

1. When a heartbeat triggers:
   - Read `memory/heartbeat-state.json` to determine priority of checks
   - Run only the most overdue check that falls within its time window
   - Update timestamp after completion
   - Maintain low token usage by using the appropriate model for each task
   - Only report when action is needed

2. After completing a check:
   - Update `memory/heartbeat-state.json` with new timestamp
   - Save any important information to daily memory file
   - Queue follow-up actions if needed

## Primary Checks

### 📋 Kanban Task Management (every 5 minutes)
- Run `/Users/karst/.openclaw/workspace/kanban-heartbeat-handler.py`
- Enforce single-task focus in the Kanban board
- Ensure task status display is current
- Alert if no tasks are in progress

### 🔄 Autonomous System (every 7 minutes)
- Run `python3 /Users/karst/.openclaw/workspace/check_messages.py` to check for messages
- Check background process status in `/Users/karst/.openclaw/workspace/autonomous_status.txt`
- Execute `python3 /Users/karst/.openclaw/workspace/process_monitor_handler.py` if any process is down

### 🔍 GlassWall Development (every 10 minutes)
- Review logs in `/Users/karst/.openclaw/workspace/logs`
- Examine recent changes in `/Users/karst/.openclaw/workspace/glasswall-rebuild`
- Continue development if needed

### 📊 API Health (every 10 minutes)
- Run health checks on all connected APIs
- Execute `python3 /Users/karst/.openclaw/workspace/autonomous/api_health_monitor.py`
- Report any failing API endpoints

### 🚀 Deployment Status (every 10 minutes)
- Check Vercel deployment status
- Review any build errors
- Deploy updates if available

### 🔧 Mission Control (every 10 minutes)
- Verify Mission Control functionality
- Fix any issues with dashboards or interfaces

### 🎛️ Command Station (every 10 minutes)
- Check command station system status
- Update components if needed

### 🔎 OpenClaw Platforms Research (every 10 minutes, 10AM-10PM only)
- Research new platforms similar to Clawn.ch
- Analyze their architecture and integration patterns
- Document findings in research files

### 🌐 Web Search (every 10 minutes, 9AM-11PM only)
- Run web searches for relevant information
- Track industry news and developments
- Look for OpenClaw updates and improvements

### 🧠 Memory Maintenance (every 10 minutes)
- Review recent conversations for context bloat
- Run `/new` when appropriate to reset context
- Summarize important information in MEMORY.md

## Task Workflow Guidelines

1. **Kanban Management Rules**:
   - Only one task should be in the "In Progress" column at a time
   - Always create a card when starting a new task
   - Move cards between columns to reflect actual status
   - Each card should have accurate progress percentage
   - Current task must be displayed in the task status banner

2. **Task Focus Approach**:
   - Complete one task before starting another when possible
   - Use "Review" column for tasks waiting for feedback
   - Move paused tasks back to "To Do" with appropriate notes
   - Document progress before switching tasks

## Scheduled Tasks

- Daily Progress Report: Every day at 9:00 AM
- Weekly Summary: Every Monday at 9:00 AM

## Task Implementation Guidelines

1. Use the most appropriate model for each task:
   - Routine checks: Use `haiku` (low cost, efficient)
   - Development/research: Use `sonnet` (better reasoning)
   - Coding: Use `deepseek` (code optimization)

2. Maintain token efficiency:
   - Keep HEARTBEAT_OK responses for routine checks
   - Only generate detailed responses when action is required
   - Use appropriate thinking level based on task complexity

3. Use isolated cron jobs for:
   - Precise schedule requirements (exact time)
   - Tasks requiring different models
   - Actions that should run independently of heartbeat

4. Use the heartbeat system for:
   - Routine monitoring tasks
   - Flexible timing requirements
   - Checks that benefit from main context

After each heartbeat check, update `memory/heartbeat-state.json` with the appropriate timestamp.