#!/bin/bash

# Script to check if Mission Control dashboard is running and restart it if needed
# Run this periodically via cron to keep the dashboard available

LOGFILE="/Users/karst/.openclaw/workspace/logs/mission-control.log"
PORT=3000

# Check if something is running on port 3000
if ! nc -z localhost $PORT >/dev/null 2>&1; then
  echo "[$(date)] Mission Control dashboard is not running. Restarting..." >> "$LOGFILE"
  
  # Kill any stuck processes
  for pid in $(lsof -t -i:$PORT 2>/dev/null); do
    echo "[$(date)] Killing stuck process $pid" >> "$LOGFILE"
    kill -9 $pid 2>/dev/null
  done
  
  # Start the server in background
  cd /Users/karst/.openclaw/workspace/mission-control
  nohup npm run start >> "$LOGFILE" 2>&1 &
  
  echo "[$(date)] Mission Control dashboard restarted with PID $!" >> "$LOGFILE"
else
  echo "[$(date)] Mission Control dashboard is running correctly" >> "$LOGFILE"
fi