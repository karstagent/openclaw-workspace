#!/bin/bash
# Setup script for memory updater cron job

# Ensure logs directory exists
mkdir -p "$HOME/.openclaw/workspace/logs"

# Make the script executable
chmod +x "$HOME/.openclaw/workspace/memory-updater.py"

# Create temporary crontab file
CRON_TMP=$(mktemp)

# Export current crontab
crontab -l > "$CRON_TMP" 2>/dev/null || echo "# Crontab for OpenClaw" > "$CRON_TMP"

# Check if entry already exists
if ! grep -q "memory-updater.py" "$CRON_TMP"; then
    # Add our cron job - runs at 5 AM every day
    echo "0 5 * * * cd $HOME/.openclaw/workspace && python3 $HOME/.openclaw/workspace/memory-updater.py >> $HOME/.openclaw/workspace/logs/memory-updater.log 2>&1" >> "$CRON_TMP"
    
    # Install the updated crontab
    crontab "$CRON_TMP"
    echo "✅ Memory updater cron job installed"
else
    echo "ℹ️ Memory updater cron job already exists"
fi

# Clean up
rm "$CRON_TMP"

echo "Done. Memory updater will run at 5 AM each day."