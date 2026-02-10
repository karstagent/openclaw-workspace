#!/bin/bash

cd /Users/karst/.openclaw/workspace/mission-control

# Make sure the tools directory exists
mkdir -p tools

# Check if Node.js is available
if command -v node &>/dev/null; then
    echo "Starting Mission Control sync service..."
    node tools/sync-service.js
else
    echo "Error: Node.js is required but not found"
    exit 1
fi