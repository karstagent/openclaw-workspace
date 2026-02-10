#!/bin/bash

# Strict Heartbeat Script with HEARTBEAT_OK handling
PROMPT="If system health is good with no critical warnings, respond EXACTLY with 'HEARTBEAT_OK'. If any critical issues exist, describe them concisely."

# Run Ollama with explicit heartbeat instructions
result=$(echo "$PROMPT" | ollama run mistral:7b-instruct)

# Check if result matches HEARTBEAT_OK
if [[ "$result" == *"HEARTBEAT_OK"* ]]; then
    echo "HEARTBEAT_OK"
else
    echo "Warning: Heartbeat detected potential issues:"
    echo "$result"
fi