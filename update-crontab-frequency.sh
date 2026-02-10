#!/bin/bash

# Update crontab frequency to ensure all autonomous functions run every 10 minutes or less

# Create a temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null

# Replace 15-minute intervals with 5-minute intervals
sed -i.bak 's/\*\/15/\*\/5/g' "$TEMP_CRONTAB"

# Install the updated crontab
crontab "$TEMP_CRONTAB"
rm "$TEMP_CRONTAB" "$TEMP_CRONTAB.bak"

echo "Updated all crontab entries to run at 5-minute intervals or less"
echo "New crontab:"
crontab -l