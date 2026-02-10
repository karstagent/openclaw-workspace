#!/bin/bash
# Run the autonomous proof test in the background

WORKSPACE="/Users/karst/.openclaw/workspace"
PYTHON_CMD="python3"
LOG_FILE="$WORKSPACE/logs/autonomous_proof_test_runner.log"

# Create logs directory if it doesn't exist
mkdir -p "$WORKSPACE/logs"

# Log start
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting autonomous proof test..." | tee -a "$LOG_FILE"

# Start the test script in the background with nohup
nohup "$PYTHON_CMD" "$WORKSPACE/autonomous_proof_test.py" > "$LOG_FILE" 2>&1 &

# Get and log the PID
PID=$!
echo "$(date '+%Y-%m-%d %H:%M:%S') - Test started with PID $PID" | tee -a "$LOG_FILE"
echo "$PID" > "$WORKSPACE/autonomous_proof_test.pid"

echo "Test is now running in the background. You can check status with:"
echo "  tail -f $LOG_FILE"
echo "Stop the test anytime with:"
echo "  kill $(cat $WORKSPACE/autonomous_proof_test.pid)"