#!/bin/bash

# This script updates the current task status in the JSON file
# Usage: ./update-task-status.sh "Your current task description"

# Get the task status from command line argument
TASK_STATUS="$1"

# File path for the task status JSON
FILE_PATH="/Users/karst/.openclaw/workspace/current-task-status.json"

# Get current timestamp in ISO format
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Create JSON content
JSON_CONTENT="{
  \"currentTaskStatus\": \"$TASK_STATUS\",
  \"lastUpdated\": \"$TIMESTAMP\"
}"

# Write to file
echo "$JSON_CONTENT" > "$FILE_PATH"

echo "Task status updated to: $TASK_STATUS"