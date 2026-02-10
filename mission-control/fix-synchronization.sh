#!/bin/bash

# Mission Control Synchronization Fix
# This script resolves synchronization issues with the Kanban board

echo "===== Mission Control Synchronization Fix ====="
echo "This script will fix synchronization issues with the Mission Control dashboard"
echo ""

# Stop any running services
echo "1. Stopping any running Next.js servers..."
pkill -f "next dev" || true
pkill -f "tools/sync-service.js" || true

# Clear Next.js cache
echo "2. Clearing Next.js cache..."
cd /Users/karst/.openclaw/workspace/mission-control
rm -rf .next || true

# Validate the API file exists
API_FILE="src/app/api/kanban-data/route.ts"
if [ ! -f "$API_FILE" ]; then
    echo "Error: API file not found at $API_FILE"
    exit 1
fi

# Start the sync service in the background
echo "3. Starting sync service..."
./start-sync-service.sh &
SYNC_PID=$!

# Sleep briefly to let the sync service start
sleep 2

# Check if the sync service is running
echo "4. Verifying sync service..."
if curl -s http://localhost:3030/status > /dev/null; then
    echo "   ✅ Sync service is running"
else
    echo "   ❌ Sync service failed to start"
    kill $SYNC_PID 2>/dev/null || true
fi

# Start the development server
echo "5. Starting development server..."
./start.sh &
DEV_PID=$!

# Sleep to let the server start
sleep 5

echo ""
echo "===== Synchronization Fix Complete ====="
echo ""
echo "Mission Control is now running with enhanced synchronization:"
echo "- Development server: http://localhost:3000 or http://localhost:3001"
echo "- Sync service status: http://localhost:3030/status"
echo ""
echo "To stop both services:"
echo "kill $SYNC_PID $DEV_PID"
echo ""