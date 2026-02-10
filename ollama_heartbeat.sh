#!/bin/bash

# Ollama Heartbeat Optimization Script

# Heartbeat Prompt
HEARTBEAT_PROMPT="Perform a quick system health check. Provide a concise report focusing on:
1. Available system resources
2. Any critical warnings
3. Potential performance bottlenecks
Output should be under 100 tokens and extremely precise."

# Run Ollama with the heartbeat prompt
echo "$HEARTBEAT_PROMPT" | ollama run mistral:7b-instruct