#!/bin/bash
# Setup script for Brave Search API

echo "Setting up Brave Search API for web search capability"
echo "You'll need a Brave Search API key from https://brave.com/search/api/"
echo ""

read -p "Enter your Brave Search API key: " BRAVE_API_KEY

# Save to environment variable for immediate use
export BRAVE_API_KEY="$BRAVE_API_KEY"

# Store in OpenClaw config
openclaw configure web.braveApiKey "$BRAVE_API_KEY"

# Also update the Gateway environment
GATEWAY_ENV_FILE="/Users/karst/.openclaw/gateway.env"

# Check if the file exists
if [ -f "$GATEWAY_ENV_FILE" ]; then
    # Check if BRAVE_API_KEY already exists in the file
    if grep -q "BRAVE_API_KEY" "$GATEWAY_ENV_FILE"; then
        # Replace existing line
        sed -i '' "s/BRAVE_API_KEY=.*/BRAVE_API_KEY=$BRAVE_API_KEY/" "$GATEWAY_ENV_FILE"
    else
        # Add new line
        echo "BRAVE_API_KEY=$BRAVE_API_KEY" >> "$GATEWAY_ENV_FILE"
    fi
else
    # Create the file
    echo "BRAVE_API_KEY=$BRAVE_API_KEY" > "$GATEWAY_ENV_FILE"
fi

echo "Brave API key has been configured!"
echo "To test, we'll need to restart the OpenClaw Gateway"
echo ""

read -p "Restart the OpenClaw Gateway now? (y/n): " RESTART_GATEWAY

if [[ "$RESTART_GATEWAY" == "y" || "$RESTART_GATEWAY" == "Y" ]]; then
    echo "Restarting Gateway..."
    openclaw gateway restart
    
    # Wait a moment for the Gateway to restart
    echo "Waiting for Gateway to restart..."
    sleep 5
    
    echo "Testing web search..."
    echo "Searching for 'OpenClaw autonomy'..."
    openclaw exec "node -e \"const util = require('util'); const exec = util.promisify(require('child_process').exec); (async () => { try { const result = await exec('openclaw eval \"web_search({ query: \\\"OpenClaw autonomy\\\" })\"'); console.log(result.stdout); } catch (e) { console.error(e.message); } })();\""
else
    echo "Gateway not restarted. You'll need to restart it manually with:"
    echo "openclaw gateway restart"
fi

echo "Setup complete!"