#!/bin/bash

# Efficient Heartbeat Script
PROMPT="Provide a system health summary in less than 100 tokens. Include CPU%, RAM usage, disk space, and a single critical warning if applicable."

# Run Ollama with token-efficient prompt
echo "$PROMPT" | ollama run mistral:7b-instruct