#!/bin/bash

LOG_DIR="/Users/karst/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/mission_control.log"

# Kill any existing mission control process
pkill -f "node.*mission-control" || true

# Start in development mode (background)
cd /Users/karst/.openclaw/workspace/mission-control
nohup npm run dev > "$LOG_FILE" 2>&1 &

# Wait for server to start
sleep 5

# Check if the server is running and get the URL
PORT=$(grep -o "localhost:[0-9]\+" "$LOG_FILE" | head -1)

if [ -n "$PORT" ]; then
  echo "Mission Control is running at http://$PORT"
  echo "Dashboard is accessible at http://$PORT/dashboard/kanban"
  echo "Logs available at $LOG_FILE"
else
  echo "Failed to start Mission Control. Check logs at $LOG_FILE"
fi