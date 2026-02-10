#!/bin/bash

# Setup Cron Job for Hourly Memory Summarizer
# This script sets up an hourly cron job for the memory summarizer

SCRIPT_PATH="/Users/karst/.openclaw/workspace/hourly-memory-summarizer.py"
LOG_DIR="/Users/karst/.openclaw/workspace/logs"
CRON_LOG="$LOG_DIR/memory-summarizer-cron.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Ensure the script is executable
chmod +x "$SCRIPT_PATH"

# Create temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Get existing crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || echo "# Memory Summarizer Cron Jobs" > "$TEMP_CRONTAB"

# Check if the cron job already exists
if grep -q "$SCRIPT_PATH" "$TEMP_CRONTAB"; then
    echo "Cron job for memory summarizer already exists."
else
    # Add the hourly cron job
    echo "# Memory Summarizer - Run hourly at minute 0" >> "$TEMP_CRONTAB"
    echo "0 * * * * /usr/bin/python3 $SCRIPT_PATH --hour \$(date +\\%H) >> $CRON_LOG 2>&1" >> "$TEMP_CRONTAB"
    
    # Install the new crontab
    crontab "$TEMP_CRONTAB"
    echo "Hourly cron job for memory summarizer has been installed."
fi

# Clean up
rm "$TEMP_CRONTAB"

echo "Setup complete. The memory summarizer will run every hour at minute 0."
echo "Logs will be written to: $CRON_LOG"
echo ""
echo "To test the summarizer immediately, run:"
echo "/usr/bin/python3 $SCRIPT_PATH --hour \$(date +%H)"