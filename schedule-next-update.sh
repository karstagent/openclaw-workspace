#!/bin/bash

# Calculate the next update time (current time + 15 minutes)
NEXT_RUN_MINS=$(( ( $(date +%s) / 60 + 15 ) * 60 ))
NEXT_RUN=$(date -r $NEXT_RUN_MINS "+%Y-%m-%d %H:%M:%S")

echo "Scheduling next Kanban update for $NEXT_RUN"

# Use the at command to schedule the next update
echo "/Users/karst/.openclaw/workspace/kanban-update-cron.sh && /Users/karst/.openclaw/workspace/schedule-next-update.sh" | at $NEXT_RUN_MINS

echo "Next update scheduled."