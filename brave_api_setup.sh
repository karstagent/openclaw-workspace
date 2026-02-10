#!/bin/bash
# Automated setup for Brave Search API

BRAVE_API_KEY="BSAZdfm0WTQjWU60kvKzc4OdIbgaKRb"

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
echo "Restarting Gateway to apply changes..."
openclaw gateway restart

echo "Setup complete!"