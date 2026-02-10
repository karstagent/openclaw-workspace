#!/bin/bash

# Setup Service for Post-Compaction Context Injector
# This script sets up a background service for the context injector

SCRIPT_PATH="/Users/karst/.openclaw/workspace/post-compaction-inject.py"
LOG_DIR="/Users/karst/.openclaw/workspace/logs"
SERVICE_LOG="$LOG_DIR/compaction-injector.log"
MONITOR_SCRIPT="/Users/karst/.openclaw/workspace/compaction-monitor.sh"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Ensure the script is executable
chmod +x "$SCRIPT_PATH"

# Create monitor script
cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash

# Compaction Monitor Script
# Continuously monitors for context compaction events

SCRIPT_PATH="/Users/karst/.openclaw/workspace/post-compaction-inject.py"
LOG_DIR="/Users/karst/.openclaw/workspace/logs"
SERVICE_LOG="$LOG_DIR/compaction-injector.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting compaction monitor service" >> "$SERVICE_LOG"

while true; do
    # This would be replaced with actual monitoring logic
    # For now, we'll just check for new session logs every 30 seconds
    
    # Find recent session logs (modified in last 2 minutes)
    RECENT_LOGS=$(find "/Users/karst/.openclaw/workspace/logs/sessions" -name "*.json" -mmin -2 2>/dev/null)
    
    if [ -n "$RECENT_LOGS" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing recent logs:" >> "$SERVICE_LOG"
        echo "$RECENT_LOGS" >> "$SERVICE_LOG"
        
        for LOG_FILE in $RECENT_LOGS; do
            SESSION_ID=$(basename "$LOG_FILE" .json)
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking for compaction in session: $SESSION_ID" >> "$SERVICE_LOG"
            
            # Run the compaction detector on this session
            python3 "$SCRIPT_PATH" --session "$SESSION_ID" >> "$SERVICE_LOG" 2>&1
        done
    fi
    
    sleep 30
done
EOF

# Make monitor script executable
chmod +x "$MONITOR_SCRIPT"

# Create launch agent plist for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.compactionmonitor.plist"
    
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.compactionmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>$MONITOR_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$SERVICE_LOG</string>
    <key>StandardErrorPath</key>
    <string>$SERVICE_LOG</string>
</dict>
</plist>
EOF
    
    # Load the launch agent
    launchctl load "$PLIST_PATH"
    echo "LaunchAgent created and loaded at: $PLIST_PATH"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Create systemd service for Linux
    SERVICE_PATH="/etc/systemd/user/compaction-monitor.service"
    
    # Check if we have sudo access
    if [ "$EUID" -ne 0 ]; then
        echo "Note: Creating user-level systemd service (non-root)"
        SERVICE_PATH="$HOME/.config/systemd/user/compaction-monitor.service"
        mkdir -p "$HOME/.config/systemd/user"
    fi
    
    cat > "$SERVICE_PATH" << EOF
[Unit]
Description=OpenClaw Context Compaction Monitor
After=network.target

[Service]
ExecStart=$MONITOR_SCRIPT
Restart=always
RestartSec=10
StandardOutput=append:$SERVICE_LOG
StandardError=append:$SERVICE_LOG

[Install]
WantedBy=default.target
EOF
    
    if [ "$EUID" -ne 0 ]; then
        # User-level service
        systemctl --user daemon-reload
        systemctl --user enable compaction-monitor.service
        systemctl --user start compaction-monitor.service
        echo "User-level systemd service created and started at: $SERVICE_PATH"
    else
        # System-level service
        systemctl daemon-reload
        systemctl enable compaction-monitor.service
        systemctl start compaction-monitor.service
        echo "System-level systemd service created and started at: $SERVICE_PATH"
    fi
    
else
    # For other systems, just run the monitor script in the background
    echo "Starting monitor script in the background"
    nohup "$MONITOR_SCRIPT" > "$SERVICE_LOG" 2>&1 &
    echo "Monitor script started with PID: $!"
    echo "To stop the service, use: kill $!"
fi

echo ""
echo "Setup complete. The compaction monitor service is now running."
echo "Logs will be written to: $SERVICE_LOG"
echo ""
echo "To test the service, simulate a context compaction with:"
echo "python3 $SCRIPT_PATH --simulate"