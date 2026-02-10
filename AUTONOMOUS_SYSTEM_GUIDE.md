# Autonomous System Usage Guide

This guide explains how to use and interact with your newly implemented fully autonomous OpenClaw system.

## Getting Started

To start the autonomous system, run:

```bash
bash /Users/karst/.openclaw/workspace/autonomous/launch_autonomous_system.sh
```

This will:
1. Initialize the memory system
2. Run API health checks
3. Set up cron jobs
4. Initialize the heartbeat system

## Key Components

### 1. Heartbeat System
- **Configuration**: `/Users/karst/.openclaw/workspace/HEARTBEAT.md`
- **State**: `/Users/karst/.openclaw/workspace/memory/heartbeat-state.json`
- **Runner**: `/Users/karst/.openclaw/workspace/autonomous/heartbeat_runner.py`

The heartbeat system uses a priority-based approach to run different checks based on when they were last run and their importance. This ensures efficient resource usage while maintaining comprehensive monitoring.

### 2. Cron Jobs
To manage cron jobs:

```bash
# List all configured cron jobs
python3 /Users/karst/.openclaw/workspace/autonomous/cron_job_manager.py list

# Set up cron jobs (if needed)
python3 /Users/karst/.openclaw/workspace/autonomous/cron_job_manager.py setup

# Remove all cron jobs
python3 /Users/karst/.openclaw/workspace/autonomous/cron_job_manager.py remove-all
```

### 3. Memory System
The memory system maintains:
- **Daily logs**: `/Users/karst/.openclaw/workspace/memory/YYYY-MM-DD.md`
- **Long-term memory**: `/Users/karst/.openclaw/workspace/MEMORY.md`

To run memory maintenance manually:
```bash
python3 /Users/karst/.openclaw/workspace/autonomous/memory_manager.py
```

### 4. API Health Monitoring
To check API health:
```bash
python3 /Users/karst/.openclaw/workspace/autonomous/api_health_monitor.py
```

### 5. Deployment Monitoring
To check GlassWall deployment:
```bash
python3 /Users/karst/.openclaw/workspace/glasswall-rebuild/check_deployment.py
```

## Status Monitoring

### Check System Status
```bash
# View current status
cat /Users/karst/.openclaw/workspace/autonomous_status.txt

# View recent messages
python3 /Users/karst/.openclaw/workspace/check_messages.py

# Check log files
ls -la /Users/karst/.openclaw/workspace/logs/
```

### Monitor Logs
Key log files:
- `/Users/karst/.openclaw/workspace/logs/heartbeat_runner.log`
- `/Users/karst/.openclaw/workspace/logs/api_health.log`
- `/Users/karst/.openclaw/workspace/logs/memory_management.log`

## Sending Messages to the System

Create a message file in the autonomous messages directory:
```bash
echo "Your message here" > /Users/karst/.openclaw/workspace/autonomous_messages/message_$(date +%Y%m%d_%H%M%S).txt
```

Or use the `send_message.py` script:
```bash
python3 /Users/karst/.openclaw/workspace/send_message.py "Your message here"
```

## Modifying the System

### Change Check Frequencies
Edit `/Users/karst/.openclaw/workspace/memory/heartbeat-state.json` to modify check frequencies:
- `checkFrequency`: How often each check should run (in seconds)
- `timeWindows`: When checks are allowed to run

### Add New Checks
To add new checks:
1. Add a new entry to `CHECK_RUNNERS` in `/Users/karst/.openclaw/workspace/autonomous/heartbeat_runner.py`
2. Add a new entry to `lastChecks` and `checkFrequency` in the state file

### Modify Model Selection
Edit `/Users/karst/.openclaw/workspace/model_selection_strategy.md` to update model selection guidelines.

## Troubleshooting

### System Not Responding
1. Check if processes are running:
```bash
python3 /Users/karst/.openclaw/workspace/process_monitor_handler.py
```

2. Check logs for errors:
```bash
grep -i "error" /Users/karst/.openclaw/workspace/logs/*.log
```

3. Restart the system:
```bash
bash /Users/karst/.openclaw/workspace/autonomous/launch_autonomous_system.sh
```

### API Issues
If APIs are experiencing issues:
```bash
python3 /Users/karst/.openclaw/workspace/autonomous/api_health_monitor.py
```

### Memory Issues
If memory files become corrupted:
```bash
python3 /Users/karst/.openclaw/workspace/autonomous/memory_manager.py
```

## Further Improvements

Consider these future enhancements:
1. Add self-updating capabilities
2. Implement anomaly detection
3. Add machine learning for pattern recognition
4. Enhance reporting and visualization
5. Implement role-based task delegation
6. Develop predictive maintenance

## Documentation

For more detailed information, refer to:
- `/Users/karst/.openclaw/workspace/AUTONOMOUS_SYSTEM_ARCHITECTURE.md`
- `/Users/karst/.openclaw/workspace/model_selection_strategy.md`
- `/Users/karst/.openclaw/workspace/HEARTBEAT.md`

## System Requirements

- OpenClaw version 2026.2.6 or higher
- Python 3.9 or higher
- Brave Search API key for web search capability
- Vercel API key for deployment monitoring (optional)