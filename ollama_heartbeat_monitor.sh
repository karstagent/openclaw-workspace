#!/bin/bash

# Ollama Heartbeat Monitor
HEARTBEAT_CONFIG="./ollama_heartbeat_config.json"
HEARTBEAT_LOG="/tmp/ollama_heartbeat_log.txt"

# Function to run heartbeat
run_heartbeat() {
    local prompt=$(jq -r '.heartbeat.prompt' "$HEARTBEAT_CONFIG")
    echo "$prompt" | ollama run mistral:7b-instruct > "$HEARTBEAT_LOG"
    
    # Optional: Send notification or take action based on log
    if grep -q "warning" "$HEARTBEAT_LOG"; then
        echo "ALERT: Potential system issue detected. Check $HEARTBEAT_LOG"
    fi
}

# Run heartbeat
run_heartbeat

# Show log contents
cat "$HEARTBEAT_LOG"