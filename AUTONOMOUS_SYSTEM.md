# Autonomous System

This system enables fully autonomous background processes that continue running even when you're not actively interacting with the bot.

## Key Components

### Background Processes

1. **persistent_runner.py**: Continuously performs GlassWall development tasks in the background
2. **github_sync.py**: Simulates GitHub synchronization and version control for autonomous development
3. **monitor.py**: Ensures all other processes stay running

### Support Systems

1. **process_monitor_handler.py**: Checks and restarts processes during scheduled cron runs
2. **send_message.py**: Handles messaging to notify about process status
3. **check_messages.py**: Retrieves messages from background processes during heartbeats
4. **start_autonomous_system.sh**: Main script to start all background processes

### Scheduled Tasks

The system includes several cron jobs:

1. **Background Process Monitor**: Runs every 30 minutes to ensure processes are running
2. **Daily Autonomous System Startup**: Runs at midnight to restart all processes
3. **GlassWall Development**: Hourly task for GlassWall project work
4. **Daily Project Report**: Daily morning report (9 AM)
5. **Research Scheduler**: Every 2 hours for ongoing research
6. **Deployment Check**: Every 4 hours to check deployment status

## How It Works

1. Background processes run continuously and generate development updates
2. The monitor ensures all processes keep running
3. Cron jobs provide scheduled triggers for various tasks
4. Heartbeats check for messages from background processes
5. System maintains status files and logs for monitoring

## Manual Commands

- Start all processes: `bash /Users/karst/.openclaw/workspace/start_autonomous_system.sh`
- Check process status: `python3 /Users/karst/.openclaw/workspace/process_monitor_handler.py`
- Check for messages: `python3 /Users/karst/.openclaw/workspace/check_messages.py`

## Status Files

- `/Users/karst/.openclaw/workspace/autonomous_status.txt` - Current system status
- `/Users/karst/.openclaw/workspace/logs/` - Log files for each component
- `/Users/karst/.openclaw/workspace/autonomous_messages/` - Message queue directory

## Troubleshooting

If processes stop running:

1. Check logs in `/Users/karst/.openclaw/workspace/logs/`
2. Run the startup script to restart everything: `bash /Users/karst/.openclaw/workspace/start_autonomous_system.sh`
3. Ensure cron jobs are enabled: Check with `openclaw cron list`