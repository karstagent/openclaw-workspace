#!/bin/bash
# Setup script for Post-Compaction Context Injector

set -e

WORKSPACE_DIR="/Users/karst/.openclaw/workspace"
SCRIPT_PATH="$WORKSPACE_DIR/post-compaction-inject.py"
TEST_SCRIPT_PATH="$WORKSPACE_DIR/test-context-injector.py"

# Ensure directories exist
mkdir -p "$WORKSPACE_DIR/logs"
mkdir -p "$WORKSPACE_DIR/memory/hourly-summaries"

# Make scripts executable
chmod +x "$SCRIPT_PATH"
chmod +x "$TEST_SCRIPT_PATH"

echo "Running tests to verify functionality..."
python3 "$TEST_SCRIPT_PATH"

echo "Setting up cron job for automated monitoring..."
openclaw cron action=add job='{
  "name": "context-compaction-monitor",
  "schedule": {
    "kind": "every",
    "everyMs": 300000
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Running context compaction monitor"
  },
  "sessionTarget": "main",
  "enabled": true
}'

echo "Installing autocorrect mechanism..."
python3 "$SCRIPT_PATH" --install-autocorrect

echo "Testing context injection generation..."
python3 "$SCRIPT_PATH" --test

echo "Setup complete! The Post-Compaction Context Injector is now operational."
echo "It will automatically detect context window compactions and inject appropriate memory."
echo ""
echo "To test manually, run:"
echo "  python3 $SCRIPT_PATH --simulate"
echo ""
echo "To force an injection for the current session, run:"
echo "  python3 $SCRIPT_PATH --inject-now --session [SESSION_ID]"
echo ""
echo "For more options, run:"
echo "  python3 $SCRIPT_PATH --help"