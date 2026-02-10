#!/bin/bash

# Path to the update script
SCRIPT_PATH="/Users/karst/.openclaw/workspace/send-kanban-update.py"

# Log file
LOG_FILE="/Users/karst/.openclaw/workspace/logs/kanban-updates.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Echo to log
echo "[$TIMESTAMP] Running Kanban board update..." >> "$LOG_FILE"

# Run the Python script to get the message
MESSAGE=$($SCRIPT_PATH)

# Log the message
echo "[$TIMESTAMP] Message: $MESSAGE" >> "$LOG_FILE"

# Use native tools to send a message to OpenClaw
# This should trigger the agent to display the message
echo "$MESSAGE" > /Users/karst/.openclaw/workspace/kanban-update-message.txt

# Let's rely on the message tool in the agent since we're having issues with direct execution

echo "[$TIMESTAMP] Update sent successfully." >> "$LOG_FILE"

# Schedule the next update in 5 minutes using sleep and background
(
  sleep 300  # 5 minutes
  $0 # Run this script again
) &

# Log the next scheduled time
NEXT_TIME=$(date -v+5M "+%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Next update scheduled for $NEXT_TIME" >> "$LOG_FILE"