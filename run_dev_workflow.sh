#!/bin/bash
# Run the development workflow for dashboard creation

echo "Starting development workflow..."

# Make the script executable
chmod +x /Users/karst/.openclaw/workspace/dev_workflow.py

# Start the workflow in the background
nohup python3 /Users/karst/.openclaw/workspace/dev_workflow.py > /Users/karst/.openclaw/workspace/dev_workflow.out 2>&1 &
WORKFLOW_PID=$!

echo "Development workflow started with PID: $WORKFLOW_PID"
echo ""
echo "This workflow will:"
echo "1. Initialize the Next.js project with proper configuration"
echo "2. Build the UI components with liquid glass aesthetics"
echo "3. Implement dashboard layout and navigation"
echo "4. Create the main dashboard pages and features"
echo "5. Add advanced functionality and optimizations"
echo "6. Complete final integration and testing"
echo ""
echo "The workflow follows proper development practices with:"
echo "- Dependency management between tasks"
echo "- Appropriate build sequence and architecture"
echo "- State persistence for resumability"
echo "- Progress tracking and reporting"
echo ""
echo "To check progress: cat /Users/karst/.openclaw/workspace/dev_workflow.log"
echo "To see current status: cat /Users/karst/.openclaw/workspace/dev_workflow_state.json"
echo ""
echo "The dashboard is being built in: /Users/karst/.openclaw/workspace/unified-dashboard"
echo ""
echo "To stop the workflow: kill $WORKFLOW_PID"

# Save the PID to a file for later reference
echo $WORKFLOW_PID > /Users/karst/.openclaw/workspace/dev_workflow.pid