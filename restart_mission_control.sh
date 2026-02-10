#!/bin/bash

# Kill only Next.js processes
echo "Stopping any existing Next.js servers..."
pkill -f "next dev"
sleep 2

# Start Next.js server with explicit port
echo "Starting Next.js server on port 3000..."
cd /Users/karst/.openclaw/workforce/mission-control && npm run dev &
sleep 5

# Check if server is running
for PORT in 3000 3001 3002; do
  echo "Checking port $PORT..."
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT)
  if [ "$RESPONSE" = "200" ]; then
    echo "Mission Control is running on port $PORT"
    echo "Opening in browser..."
    open http://localhost:$PORT
    echo "Mission Control is now ready to use."
    exit 0
  fi
done

echo "Failed to start server. Please check logs."