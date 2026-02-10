#!/bin/bash

# Function to get download progress
get_progress() {
    ollama pull mistral:7b-instruct 2>&1 | grep -E '%' | tail -n 1 | sed -E 's/.*([0-9]+%).*/\1/'
}

# Function to get download speed and estimated time
get_speed_and_time() {
    ollama pull mistral:7b-instruct 2>&1 | grep -E 'MB/s' | tail -n 1
}

# Initial message
echo "Starting Mistral 7B model download monitoring..."

# Monitor loop
while true; do
    progress=$(get_progress)
    speed=$(get_speed_and_time)
    echo "Progress: $progress | $speed"
    sleep 60
done