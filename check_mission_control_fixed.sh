#!/bin/bash

# Kill existing processes
echo "Stopping any existing Next.js and Convex servers..."
pkill -f "next dev"
pkill -f "convex dev"
sleep 2

# Start Convex server
echo "Starting Convex server..."
cd /Users/karst/.openclaw/workforce/mission-control && npx convex dev &
sleep 3

# Start Next.js server with explicit port
echo "Starting Next.js server on port 3001..."
cd /Users/karst/.openclaw/workforce/mission-control && PORT=3001 npm run dev &
sleep 5

# Check if Next.js server started on port 3001
echo "Checking if server is running on port 3001..."
curl -s -I http://localhost:3001 > /dev/null
if [ $? -eq 0 ]; then
    echo "Mission Control is running on port 3001"
    echo "Opening in browser..."
    open http://localhost:3001
else
    echo "Failed to start server on port 3001. Checking port 3000..."
    curl -s -I http://localhost:3000 > /dev/null
    if [ $? -eq 0 ]; then
        echo "Mission Control is running on port 3000"
        echo "Opening in browser..."
        open http://localhost:3000
    else
        echo "Failed to start server on expected ports. Please check logs."
        exit 1
    fi
fi

echo "Mission Control is now ready to use."