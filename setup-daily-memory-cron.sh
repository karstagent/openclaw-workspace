#!/bin/bash
# Setup script for daily memory aggregator cron job

# Ensure logs directory exists
mkdir -p "$HOME/.openclaw/workspace/logs"
mkdir -p "$HOME/.openclaw/workspace/memory/hourly"

# Make the script executable
chmod +x "$HOME/.openclaw/workspace/daily-memory-aggregator.py"

# Create temporary crontab file
CRON_TMP=$(mktemp)

# Export current crontab
crontab -l > "$CRON_TMP" 2>/dev/null || echo "# Crontab for OpenClaw" > "$CRON_TMP"

# Check if entry already exists
if ! grep -q "daily-memory-aggregator.py" "$CRON_TMP"; then
    # Add our cron job - runs at 11:59 PM every day
    echo "59 23 * * * cd $HOME/.openclaw/workspace && python3 $HOME/.openclaw/workspace/daily-memory-aggregator.py >> $HOME/.openclaw/workspace/logs/daily-memory-cron.log 2>&1" >> "$CRON_TMP"
    
    # Install the updated crontab
    crontab "$CRON_TMP"
    echo "✅ Daily memory aggregator cron job installed"
else
    echo "ℹ️ Daily memory aggregator cron job already exists"
fi

# Clean up
rm "$CRON_TMP"

echo "Done. Daily memory aggregator will run at 11:59 PM each day."