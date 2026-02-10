#!/bin/bash

# File to store the last known progress
PROGRESS_FILE="/tmp/ollama_download_progress.txt"

# Function to get download progress
get_progress() {
    # Capture the last progress line
    progress_line=$(ollama pull mistral:7b-instruct 2>&1 | grep -E '%' | tail -n 1)
    
    # If a progress line was found, extract the percentage and speed
    if [ -n "$progress_line" ]; then
        percentage=$(echo "$progress_line" | sed -E 's/.*([0-9]+%).*/\1/')
        speed=$(echo "$progress_line" | grep -oE '[0-9]+(\.[0-9]+)? MB/s')
        total_size=$(echo "$progress_line" | grep -oE '[0-9]+(\.[0-9]+)? GB/[0-9]+(\.[0-9]+)? GB')
        
        # Save progress to file
        echo "Progress: $percentage | Speed: $speed | Total: $total_size" > "$PROGRESS_FILE"
        
        # Output to console
        cat "$PROGRESS_FILE"
    else
        # If no progress line, read from last saved progress
        if [ -f "$PROGRESS_FILE" ]; then
            cat "$PROGRESS_FILE"
        else
            echo "Download not started or progress unknown"
        fi
    fi
}

# Run initial check
get_progress