#!/bin/bash
# Test script for the Post-Compaction Context Injector

# Ensure logs directory exists
mkdir -p "$HOME/.openclaw/workspace/logs"

echo "=== Testing Post-Compaction Context Injector ==="

# Run with --show to display what would be injected
echo "Running in show mode (no actual injection)..."
python3 "$HOME/.openclaw/workspace/post-compaction-inject.py" --show --force

# Check the logs
echo ""
echo "=== Recent Log Entries ==="
tail -20 "$HOME/.openclaw/workspace/logs/post-compaction-inject.log"

echo ""
echo "=== Test Complete ==="