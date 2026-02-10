#!/bin/bash

# Full path to the virtual environment Python
VENV_PYTHON="/Users/karst/.openclaw/venv/bin/python3"

# Ensure the virtual environment is up to date
$VENV_PYTHON -m pip install schedule requests

# Run the heartbeat scheduler
nohup $VENV_PYTHON /Users/karst/.openclaw/workspace/heartbeat_scheduler.py > /tmp/heartbeat_scheduler.log 2>&1 &

# Print the process ID
echo "Heartbeat scheduler started. PID: $!"