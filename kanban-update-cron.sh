#!/bin/bash

# Script to update the Kanban board and send a visible message to the chat
# This will be more obvious than background checks

# Log file
LOG_FILE="/Users/karst/.openclaw/workspace/logs/kanban-updates.log"

# Current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Echo to log
echo "[$TIMESTAMP] Running Kanban board update check..." >> "$LOG_FILE"

# Update the Kanban board using the task manager
/Users/karst/.openclaw/workspace/kanban-task-manager.py --enforce >> "$LOG_FILE" 2>&1

# Check current task progress
IN_PROGRESS_TASK=$(python3 -c "
import json
with open('/Users/karst/.openclaw/workspace/kanban-board.json', 'r') as f:
    data = json.load(f)
for column in data.get('columns', []):
    if column.get('id') == 'in-progress':
        tasks = column.get('tasks', [])
        if tasks:
            task = tasks[0]  # Get the first task
            print(f\"Current task: {task.get('title')} ({task.get('progress', 0)}% complete)\")
            break
")

# Update the current task status
if [ ! -z "$IN_PROGRESS_TASK" ]; then
    /Users/karst/.openclaw/workspace/task-status-updater.py "$IN_PROGRESS_TASK" >> "$LOG_FILE" 2>&1
fi

# Create a message file that will be noticed in the next interaction
KANBAN_MESSAGE="/Users/karst/.openclaw/workspace/kanban-update-message.txt"
echo "🔄 AUTOMATED KANBAN UPDATE ($TIMESTAMP): 
$IN_PROGRESS_TASK
Next update in 15 minutes." > "$KANBAN_MESSAGE"

# The file will be read and displayed by the agent during the next interaction

echo "[$TIMESTAMP] Kanban update completed and notification sent." >> "$LOG_FILE"