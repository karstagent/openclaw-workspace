#!/bin/bash
# Setup script for hourly memory summarizer cron job

# Ensure logs directory exists
mkdir -p "$HOME/.openclaw/workspace/logs"
mkdir -p "$HOME/.openclaw/workspace/memory/hourly"

# Make the script executable
chmod +x "$HOME/.openclaw/workspace/hourly-memory-summarizer.py"

# Create temporary crontab file
CRON_TMP=$(mktemp)

# Export current crontab
crontab -l > "$CRON_TMP" 2>/dev/null || echo "# Crontab for OpenClaw" > "$CRON_TMP"

# Check if entry already exists
if ! grep -q "hourly-memory-summarizer.py" "$CRON_TMP"; then
    # Add our cron job - runs at the beginning of every hour
    echo "0 * * * * cd $HOME/.openclaw/workspace && python3 $HOME/.openclaw/workspace/hourly-memory-summarizer.py >> $HOME/.openclaw/workspace/logs/hourly-memory-cron.log 2>&1" >> "$CRON_TMP"
    
    # Install the updated crontab
    crontab "$CRON_TMP"
    echo "✅ Hourly memory summarizer cron job installed"
else
    echo "ℹ️ Hourly memory summarizer cron job already exists"
fi

# Clean up
rm "$CRON_TMP"

echo "Done. Hourly memory summarizer will run at the beginning of each hour."