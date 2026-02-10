#!/bin/bash

# Script to ensure Kanban board data is properly synchronized
# This script will restart the development server and clear any caches

echo "=== Mission Control Synchronization Tool ==="
echo "This will restart the development server and ensure data synchronization"

# Stop any running Next.js servers
echo "Stopping any running Next.js servers..."
pkill -f "next dev" || true

# Clear Next.js cache
echo "Clearing Next.js cache..."
cd /Users/karst/.openclaw/workspace/mission-control
rm -rf .next || true

# Restart the server
echo "Starting development server..."
./start.sh

echo "Done! Mission Control should now be properly synchronized."