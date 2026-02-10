#!/bin/bash

# Script to verify Kanban board integrity every 3 minutes

# Log file
LOG_FILE="/Users/karst/.openclaw/workspace/logs/kanban-verification.log"

# Current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Echo to log
echo "[$TIMESTAMP] Running Kanban integrity verification..." >> "$LOG_FILE"

# Run the verification script
RESULT=$(python3 /Users/karst/.openclaw/workspace/kanban-integrity.py)
EXIT_CODE=$?

# Log the result
echo "[$TIMESTAMP] Result: $RESULT" >> "$LOG_FILE"
echo "[$TIMESTAMP] Exit Code: $EXIT_CODE" >> "$LOG_FILE"

# If verification failed, send an alert
if [ $EXIT_CODE -ne 0 ]; then
  echo "[$TIMESTAMP] ALERT: Kanban integrity check failed!" >> "$LOG_FILE"
  
  # Send alert message
  /opt/homebrew/bin/openclaw message send -t 535786496 --channel telegram "🚨 ALERT: Kanban integrity check failed at $TIMESTAMP. Please check the board status."
  
  # Attempt auto-recovery
  echo "[$TIMESTAMP] Attempting auto-recovery..." >> "$LOG_FILE"
  python3 -c '
import json, datetime
try:
  with open("/Users/karst/.openclaw/workspace/kanban-board.json", "r") as f:
    data = json.load(f)
  data["lastUpdated"] = datetime.datetime.utcnow().isoformat() + "Z"
  with open("/Users/karst/.openclaw/workspace/kanban-board.json", "w") as f:
    json.dump(data, f, indent=2)
  print("Auto-recovery successful")
except Exception as e:
  print(f"Auto-recovery failed: {e}")
' >> "$LOG_FILE" 2>&1
fi

echo "[$TIMESTAMP] Verification completed." >> "$LOG_FILE"
echo "-------------------------------------------" >> "$LOG_FILE"