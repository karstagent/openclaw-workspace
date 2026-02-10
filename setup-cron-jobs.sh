#!/bin/bash

echo "Setting up cron jobs for Kanban management and heartbeat system..."

# Generate a temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null

# Add the Kanban heartbeat job if it doesn't exist
if ! grep -q "kanban-heartbeat-handler.py" "$TEMP_CRONTAB"; then
  echo "# Run Kanban task management heartbeat check every 15 minutes" >> "$TEMP_CRONTAB"
  echo "*/15 * * * * /Users/karst/.openclaw/workspace/kanban-heartbeat-handler.py >> /Users/karst/.openclaw/workspace/logs/kanban-heartbeat.log 2>&1" >> "$TEMP_CRONTAB"
  echo "Added Kanban heartbeat job"
fi

# Add the heartbeat runner job if it doesn't exist
if ! grep -q "heartbeat-runner.py" "$TEMP_CRONTAB"; then
  echo "# Run intelligent heartbeat system every 5 minutes" >> "$TEMP_CRONTAB"
  echo "*/5 * * * * /Users/karst/.openclaw/workspace/heartbeat-runner.py >> /Users/karst/.openclaw/workspace/logs/heartbeat-runner.log 2>&1" >> "$TEMP_CRONTAB"
  echo "Added heartbeat runner job"
fi

# Add the Mission Control dashboard health check if it doesn't exist
if ! grep -q "ensure_mission_control_running.sh" "$TEMP_CRONTAB"; then
  echo "# Ensure Mission Control dashboard is running every 5 minutes" >> "$TEMP_CRONTAB"
  echo "*/5 * * * * /Users/karst/.openclaw/workspace/ensure_mission_control_running.sh" >> "$TEMP_CRONTAB"
  echo "Added Mission Control health check job"
fi

# Install the new crontab
crontab "$TEMP_CRONTAB"
rm "$TEMP_CRONTAB"

# Create logs directory if it doesn't exist
mkdir -p /Users/karst/.openclaw/workspace/logs

echo "Cron jobs have been set up successfully."
echo "Logs will be written to /Users/karst/.openclaw/workspace/logs/"