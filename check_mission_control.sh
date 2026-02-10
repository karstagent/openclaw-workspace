#!/bin/bash

# Check if mission control is running
if pgrep -f "node.*mission-control" > /dev/null; then
    echo "Mission Control is running."
    
    # Try to get the port from the log file
    LOG_FILE="/Users/karst/.openclaw/workspace/logs/mission_control.log"
    if [ -f "$LOG_FILE" ]; then
        PORT=$(grep -o "localhost:[0-9]\+" "$LOG_FILE" | head -1)
        if [ -n "$PORT" ]; then
            echo "Dashboard is accessible at http://$PORT/dashboard/kanban"
        else
            echo "Port information not found in logs."
        fi
    else
        echo "Log file not found."
    fi
else
    echo "Mission Control is not running."
    echo "Run /Users/karst/.openclaw/workspace/start_mission_control.sh to start it."
fi