#!/bin/bash

echo "Setting up visible Kanban update cron job..."

# Generate a temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null

# Add the visible Kanban update job if it doesn't exist
if ! grep -q "kanban-update-cron.sh" "$TEMP_CRONTAB"; then
  echo "# Run visible Kanban update every 15 minutes" >> "$TEMP_CRONTAB"
  echo "*/15 * * * * /Users/karst/.openclaw/workspace/kanban-update-cron.sh" >> "$TEMP_CRONTAB"
  echo "Added visible Kanban update job"
fi

# Install the new crontab
crontab "$TEMP_CRONTAB"
rm "$TEMP_CRONTAB"

echo "Visible Kanban update cron job has been set up successfully."
echo "You will receive Telegram messages every 15 minutes with Kanban updates."