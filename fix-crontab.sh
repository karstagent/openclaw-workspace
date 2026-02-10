#!/bin/bash

# First, create the temp file
TEMP_FILE="/Users/karst/.openclaw/workspace/current_crontab.txt"

# Get current crontab
crontab -l > "$TEMP_FILE" 2>/dev/null

# See if our job is already there
if ! grep -q "kanban-update-cron.sh" "$TEMP_FILE"; then
  # Add our job
  echo "# Run visible Kanban update every 5 minutes" >> "$TEMP_FILE"
  echo "*/5 * * * * /Users/karst/.openclaw/workspace/kanban-update-cron.sh" >> "$TEMP_FILE"
  
  # Install the updated crontab
  cat "$TEMP_FILE" | crontab -
  
  echo "Added Kanban update job to crontab."
else
  echo "Kanban update job already exists in crontab."
fi

# Clean up
rm -f "$TEMP_FILE"

# Verify the crontab was updated
echo "Current crontab:"
crontab -l