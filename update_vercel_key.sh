#!/bin/bash
# Script to update Vercel API key in environment and Gateway config

# The new Vercel API key
# Replace this with your actual API key when running the script
VERCEL_API_KEY="YOUR_VERCEL_API_KEY"

# Export for immediate use in current session
export VERCEL_API_KEY="$VERCEL_API_KEY"

# Update Gateway environment file
GATEWAY_ENV_FILE="/Users/karst/.openclaw/gateway.env"

# Check if the file exists
if [ -f "$GATEWAY_ENV_FILE" ]; then
    # Check if VERCEL_API_KEY already exists in the file
    if grep -q "VERCEL_API_KEY" "$GATEWAY_ENV_FILE"; then
        # Replace existing line
        sed -i '' "s/VERCEL_API_KEY=.*/VERCEL_API_KEY=$VERCEL_API_KEY/" "$GATEWAY_ENV_FILE"
        echo "Updated existing VERCEL_API_KEY in $GATEWAY_ENV_FILE"
    else
        # Add new line
        echo "VERCEL_API_KEY=$VERCEL_API_KEY" >> "$GATEWAY_ENV_FILE"
        echo "Added VERCEL_API_KEY to $GATEWAY_ENV_FILE"
    fi
else
    # Create the file
    echo "VERCEL_API_KEY=$VERCEL_API_KEY" > "$GATEWAY_ENV_FILE"
    echo "Created $GATEWAY_ENV_FILE with VERCEL_API_KEY"
fi

echo "Vercel API key has been updated in environment variables and gateway.env"
echo "To apply changes, the OpenClaw Gateway needs to be restarted"

# Ask to restart the gateway
read -p "Restart the OpenClaw Gateway now? (y/n): " RESTART_GATEWAY

if [[ "$RESTART_GATEWAY" == "y" || "$RESTART_GATEWAY" == "Y" ]]; then
    echo "Restarting Gateway..."
    openclaw gateway restart
    
    # Wait a moment for the Gateway to restart
    echo "Waiting for Gateway to restart..."
    sleep 5
    
    echo "Gateway has been restarted with the new Vercel API key"
else
    echo "Gateway not restarted. You'll need to restart it manually with:"
    echo "openclaw gateway restart"
fi

echo "Testing Vercel API access..."
curl -s -H "Authorization: Bearer $VERCEL_API_KEY" "https://api.vercel.com/v1/projects" | head -20

echo "Setup complete!"