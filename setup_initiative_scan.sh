#!/bin/bash

# Schedule the daily initiative scan
# This script sets up a cron job to run the initiative scanner daily

# Ensure the script exists and is executable
SCAN_SCRIPT="/Users/karst/.openclaw/workspace/daily_initiative_scan.py"
if [ ! -f "$SCAN_SCRIPT" ]; then
    echo "Error: Cannot find $SCAN_SCRIPT"
    exit 1
fi

chmod +x "$SCAN_SCRIPT"
echo "Made script executable: $SCAN_SCRIPT"

# Create a temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || echo "# New crontab" > "$TEMP_CRONTAB"

# Check if the job already exists
if grep -q "daily_initiative_scan.py" "$TEMP_CRONTAB"; then
    echo "Initiative scan is already scheduled in crontab"
else
    # Add our job - run at 8:00 AM every day
    echo "0 8 * * * $SCAN_SCRIPT >> /Users/karst/.openclaw/workspace/logs/initiative-scan-cron.log 2>&1" >> "$TEMP_CRONTAB"
    
    # Install the new crontab
    crontab "$TEMP_CRONTAB"
    echo "Scheduled initiative scan to run daily at 8:00 AM"
fi

# Clean up
rm "$TEMP_CRONTAB"

# Create an entry in the memory file for this setup
MEMORY_DIR="/Users/karst/.openclaw/workspace/memory"
TODAY=$(date +"%Y-%m-%d")
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"

if [ ! -d "$MEMORY_DIR" ]; then
    mkdir -p "$MEMORY_DIR"
fi

# Append to today's memory file if it exists, otherwise create it
if [ -f "$MEMORY_FILE" ]; then
    echo -e "\n## Autonomous Initiative System Setup\n" >> "$MEMORY_FILE"
    echo "- Set up daily initiative scan to run at 8:00 AM" >> "$MEMORY_FILE"
    echo "- Created automated task identification system" >> "$MEMORY_FILE"
    echo "- Established metrics for tracking autonomous behavior" >> "$MEMORY_FILE"
    echo -e "- Files created:\n  - daily_initiative_scan.py\n  - AUTONOMOUS_BEHAVIOR_PATTERNS.md\n  - AUTONOMOUS_METRICS.md" >> "$MEMORY_FILE"
else
    echo -e "# Memory Entry $TODAY\n" > "$MEMORY_FILE"
    echo -e "## Autonomous Initiative System Setup\n" >> "$MEMORY_FILE"
    echo "- Set up daily initiative scan to run at 8:00 AM" >> "$MEMORY_FILE"
    echo "- Created automated task identification system" >> "$MEMORY_FILE"
    echo "- Established metrics for tracking autonomous behavior" >> "$MEMORY_FILE"
    echo -e "- Files created:\n  - daily_initiative_scan.py\n  - AUTONOMOUS_BEHAVIOR_PATTERNS.md\n  - AUTONOMOUS_METRICS.md" >> "$MEMORY_FILE"
fi

echo "Updated memory file with setup information"
echo "Setup complete!"