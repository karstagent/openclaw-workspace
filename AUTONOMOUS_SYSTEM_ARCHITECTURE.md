# Autonomous System Architecture

This document outlines the architecture of the fully autonomous OpenClaw agent system.

## Core Components

### 1. Heartbeat System
- **Main Controller**: `/Users/karst/.openclaw/workspace/autonomous/heartbeat_runner.py`
- **State File**: `/Users/karst/.openclaw/workspace/memory/heartbeat-state.json`
- **Configuration**: `/Users/karst/.openclaw/workspace/HEARTBEAT.md`

The heartbeat system uses a rotating priority-based approach to determine which check to run at each heartbeat interval. Rather than running all checks on every heartbeat (which would be inefficient and expensive), it selects the most overdue check that falls within its allowed time window.

Each check has:
- A frequency (how often it should run)
- A time window (when it's allowed to run)
- A recommended model and thinking level
- A specific command to execute

### 2. Cron Job System
- **Manager**: `/Users/karst/.openclaw/workspace/autonomous/cron_job_manager.py`
- **Scheduled Jobs**:
  - Daily Progress Report (9 AM daily)
  - API Health Check (every 3 hours)
  - Memory Maintenance (2 AM daily)
  - Weekly Summary (Monday 9 AM)
  - Platform Research (Tuesday and Friday 11 AM)

Cron jobs handle precisely scheduled tasks that need to run at specific times, regardless of the heartbeat system. They use isolated sessions to avoid cluttering the main conversation context.

### 3. Memory Management
- **Manager**: `/Users/karst/.openclaw/workspace/autonomous/memory_manager.py`
- **Daily Files**: `/Users/karst/.openclaw/workspace/memory/YYYY-MM-DD.md`
- **Long-term Memory**: `/Users/karst/.openclaw/workspace/MEMORY.md`

The memory system maintains daily log files and periodically updates the long-term memory file with important information. This ensures that knowledge persists across sessions and that the agent can refer to past events and decisions.

### 4. Health Monitoring
- **API Monitor**: `/Users/karst/.openclaw/workspace/autonomous/api_health_monitor.py`
- **Process Monitor**: `/Users/karst/.openclaw/workspace/process_monitor_handler.py`
- **Status File**: `/Users/karst/.openclaw/workspace/autonomous_status.txt`

Health monitoring components check the status of critical APIs, background processes, and services. When issues are detected, they send notifications through the autonomous message system.

### 5. Message System
- **Message Directory**: `/Users/karst/.openclaw/workspace/autonomous_messages/`
- **Message Checker**: `/Users/karst/.openclaw/workspace/check_messages.py`

Components can send notifications by creating message files in the autonomous_messages directory. The check_messages.py script is run during heartbeats to check for and process these messages.

### 6. Project-Specific Systems
- **GlassWall Deployment**: `/Users/karst/.openclaw/workspace/glasswall-rebuild/check_deployment.py`
- **Development Workflow**: `/Users/karst/.openclaw/workspace/dev_workflow.py`

Project-specific components handle tasks related to particular projects, such as checking deployment status, monitoring development progress, and managing project-specific resources.

## Model Selection Strategy

The system uses an intelligent model selection strategy to balance cost and capability:

- **Haiku** (Claude 3.5 Haiku): Used for routine tasks, status checks, and background processes
- **Sonnet** (Claude 3.7 Sonnet): Used for complex analysis, strategic thinking, and important communications
- **DeepSeek** (DeepSeek Coder): Used for code-related tasks and technical development

See `/Users/karst/.openclaw/workspace/model_selection_strategy.md` for detailed guidelines.

## Startup and Initialization

The unified launch script `/Users/karst/.openclaw/workspace/autonomous/launch_autonomous_system.py` initializes all components:

1. Prepares the memory system
2. Runs initial API health checks
3. Sets up cron jobs
4. Initializes the heartbeat system

## Configuration

Key configuration files:
- **HEARTBEAT.md**: Defines the tasks performed during heartbeats
- **heartbeat-state.json**: Tracks when checks were last run and their frequencies
- **model_selection_strategy.md**: Guidelines for model selection
- **SOUL.md**: Core principles and autonomous behavior guidelines

## Reliability Features

The autonomous system includes several reliability features:

1. **Self-monitoring**: Components monitor their own status and the status of other components
2. **Fault recovery**: When issues are detected, components attempt to recover
3. **Redundancy**: Critical checks are performed through multiple mechanisms
4. **Logging**: Detailed logs are maintained for all components
5. **State persistence**: State is persisted across restarts
6. **Time window constraints**: Tasks only run during appropriate time windows
7. **Priority-based scheduling**: Resources are allocated based on priority

## Recommended Operation

To ensure optimal operation:

1. Run `/Users/karst/.openclaw/workspace/autonomous/launch_autonomous_system.sh` during system startup
2. Check `/Users/karst/.openclaw/workspace/autonomous_status.txt` for current status
3. Review logs in `/Users/karst/.openclaw/workspace/logs/` for detailed activity records
4. Use the message system to send instructions to the autonomous system

## Future Improvements

Planned enhancements to the autonomous system:

1. Add self-updating capabilities
2. Implement more sophisticated anomaly detection
3. Add machine learning components for pattern recognition
4. Improve coordination between components
5. Enhance the reporting and visualization systems
6. Implement role-based task delegation
7. Develop predictive maintenance capabilities