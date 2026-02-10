#!/bin/bash

# Logging
LOGFILE="/tmp/heartbeat_debug.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" >> "$LOGFILE"
}

# Start logging
log "Heartbeat script started"

# Generate Timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="8321959949:AAFe7LZrQLe5XaqWfHWoRjrNlZL7PW5vmPA"
TELEGRAM_CHAT_ID="535786496"

# Heartbeat Report Generation
generate_report() {
    local report=$(cat <<EOF
🕰️ SYSTEM HEARTBEAT REPORT 🕰️
Timestamp: $TIMESTAMP

🔹 WHAT I'VE DONE:
- Installed QMD skill repository
- Set up local embedding environment
- Created background task script

🔹 WHAT I'M DOING NOW:
- Monitoring system resources
- Maintaining workspace organization
- Preparing for potential new tasks

🔹 WHAT I PLAN TO DO:
- Continue refining local embedding strategy
- Explore integration of QMD skill
- Optimize token usage mechanisms

💻 SYSTEM HEALTH:
Disk Space: $(df -h / | awk '/\// {print $5}')
CPU Cores: $(sysctl -n hw.ncpu)
Memory Total: $(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')

🌟 LAYMAN'S EXPLANATION:
Think of me like a super-efficient personal assistant. Right now, I'm working on making our AI system smarter and cheaper to run.
EOF
)

    # Log the report
    log "Generated report: $report"

    # Send Telegram notification
    local response=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
         -d "chat_id=$TELEGRAM_CHAT_ID" \
         -d "text=$report")
    
    # Log Telegram response
    log "Telegram API response: $response"
}

# Run the report
generate_report

# Log script completion
log "Heartbeat script completed"