#!/bin/bash
# Quick start script for dashboard development
# This starts both the system monitor and task manager directly

echo "Starting autonomous dashboard development..."

# Start the system monitor in the background
python3 /Users/karst/.openclaw/workspace/autonomous/system_monitor.py > /Users/karst/.openclaw/workspace/autonomous/logs/system_monitor.log 2>&1 &
MONITOR_PID=$!
echo "System monitor started with PID $MONITOR_PID"

# Give the monitor time to initialize
sleep 2

# Start the task manager in the background
python3 /Users/karst/.openclaw/workspace/autonomous/task_manager.py > /Users/karst/.openclaw/workspace/autonomous/logs/task_manager.log 2>&1 &
TASK_MANAGER_PID=$!
echo "Task manager started with PID $TASK_MANAGER_PID"

# Start the continuous runner in the background
python3 /Users/karst/.openclaw/workspace/autonomous/continuous_runner.py > /Users/karst/.openclaw/workspace/autonomous/logs/continuous_runner.log 2>&1 &
RUNNER_PID=$!
echo "Continuous runner started with PID $RUNNER_PID"

echo ""
echo "Autonomous dashboard development is now running!"
echo "The system will continue working in the background, building the dashboard at:"
echo "/Users/karst/.openclaw/workspace/unified-dashboard/"
echo ""
echo "To check progress:"
echo "python3 /Users/karst/.openclaw/workspace/autonomous/status_reporter.py"
echo ""
echo "Process IDs for monitoring:"
echo "System Monitor: $MONITOR_PID"
echo "Task Manager: $TASK_MANAGER_PID"
echo "Continuous Runner: $RUNNER_PID"