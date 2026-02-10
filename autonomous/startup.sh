#!/bin/bash
# Autonomous System Startup Script
# Run this script to start the autonomous system
# Can be added to system startup

echo "Starting autonomous system at $(date)"

# Change to the script directory
cd /Users/karst/.openclaw/workspace/autonomous

# Start the system monitor
python3 /Users/karst/.openclaw/workspace/autonomous/system_monitor.py &

echo "System monitor started with PID $!"
echo "Autonomous system startup complete"
