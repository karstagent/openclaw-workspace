#!/bin/bash
# Run the autonomous dashboard builder

echo "Starting autonomous dashboard builder..."

# Start the builder in the background
nohup python3 /Users/karst/.openclaw/workspace/autonomous_builder.py > /Users/karst/.openclaw/workspace/autonomous_builder.out 2>&1 &
BUILDER_PID=$!

echo "Autonomous builder started with PID: $BUILDER_PID"
echo "Process will run continuously in the background."
echo "Sending regular API calls to OpenClaw to build the unified dashboard."
echo
echo "To check progress: cat /Users/karst/.openclaw/workspace/autonomous_builder.log"
echo "To check status: cat /Users/karst/.openclaw/workspace/autonomous_builder_status.json"
echo
echo "The dashboard will be built in: /Users/karst/.openclaw/workspace/unified-dashboard"
echo
echo "To stop the builder: kill $BUILDER_PID"

# Save the PID to a file for later reference
echo $BUILDER_PID > /Users/karst/.openclaw/workspace/autonomous_builder.pid