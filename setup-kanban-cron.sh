#!/bin/bash

echo "Setting up Kanban integrity monitoring cron jobs..."

# Generate a temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null

# Remove existing Kanban jobs if they exist
grep -v "verify_kanban_integrity.sh" "$TEMP_CRONTAB" | grep -v "kanban-heartbeat-handler.py" > "${TEMP_CRONTAB}.new"
mv "${TEMP_CRONTAB}.new" "$TEMP_CRONTAB"

# Add the Kanban integrity verification job (every 3 minutes)
echo "# Run Kanban board integrity verification every 3 minutes" >> "$TEMP_CRONTAB"
echo "*/3 * * * * /Users/karst/.openclaw/workspace/verify_kanban_integrity.sh" >> "$TEMP_CRONTAB"

# Add the Kanban heartbeat job (every 15 minutes)
echo "# Run Kanban task management heartbeat check every 15 minutes" >> "$TEMP_CRONTAB"
echo "*/15 * * * * /Users/karst/.openclaw/workspace/kanban-heartbeat-handler.py >> /Users/karst/.openclaw/workspace/logs/kanban-heartbeat.log 2>&1" >> "$TEMP_CRONTAB"

# Install the new crontab
crontab "$TEMP_CRONTAB"
rm "$TEMP_CRONTAB"

# Create logs directory if it doesn't exist
mkdir -p /Users/karst/.openclaw/workspace/logs

echo "Kanban monitoring cron jobs have been set up successfully."
echo "- Integrity verification: Every 3 minutes"
echo "- Heartbeat checks: Every 15 minutes"
echo "Logs will be written to /Users/karst/.openclaw/workspace/logs/"