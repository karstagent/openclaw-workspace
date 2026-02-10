#!/bin/bash
# Autonomous System Starter
# This script starts all the background processes needed for autonomous operation

# Set up constants
WORKSPACE="/Users/karst/.openclaw/workspace"
LOGS_DIR="$WORKSPACE/logs"
PYTHON_CMD="python3"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGS_DIR/startup.log"
}

# Function to start a Python script
start_script() {
    local script_name="$1"
    local script_path="$WORKSPACE/$script_name"
    
    log_message "Starting $script_name..."
    
    # Make sure the script is executable
    chmod +x "$script_path"
    
    # Start the script with nohup to ensure it stays running after terminal closes
    nohup "$PYTHON_CMD" "$script_path" > "$LOGS_DIR/${script_name}.log" 2>&1 &
    
    # Get the PID
    local pid=$!
    log_message "$script_name started with PID $pid"
    
    # Store the PID
    echo "$pid" > "$WORKSPACE/${script_name}.pid"
    
    # Return true if the process is running
    ps -p $pid > /dev/null
}

# Function to check if a script is running
is_script_running() {
    local script_name="$1"
    
    # Use pgrep to find the process
    if pgrep -f "$script_name" > /dev/null; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Notify via Telegram
send_notification() {
    local message="$1"
    
    log_message "Sending notification: $message"
    
    # Use our Python utility script for messaging
    python3 "$WORKSPACE/send_message.py" "$message"
}

# Start notification
log_message "Starting autonomous system..."
send_notification "🚀 Autonomous System: Starting background processes..."

# Start the scripts
SCRIPTS=("persistent_runner.py" "github_sync.py" "monitor.py")
STARTED=0
FAILED=0

for script in "${SCRIPTS[@]}"; do
    if is_script_running "$script"; then
        log_message "$script is already running"
    else
        if start_script "$script"; then
            log_message "Successfully started $script"
            STARTED=$((STARTED + 1))
        else
            log_message "Failed to start $script"
            FAILED=$((FAILED + 1))
        fi
    fi
    
    # Small delay between script starts
    sleep 2
done

# Final status message
STATUS_MESSAGE="🔄 Autonomous System Status:\n"
STATUS_MESSAGE+="✅ Started $STARTED new processes\n"
if [ $FAILED -gt 0 ]; then
    STATUS_MESSAGE+="❌ Failed to start $FAILED processes\n"
else
    STATUS_MESSAGE+="✅ All processes started successfully\n"
fi

# List running processes
STATUS_MESSAGE+="\nRunning processes:\n"
for script in "${SCRIPTS[@]}"; do
    if is_script_running "$script"; then
        STATUS_MESSAGE+="• $script: ✅ Running\n"
    else
        STATUS_MESSAGE+="• $script: ❌ Not running\n"
    fi
done

# Send the status message
send_notification "$STATUS_MESSAGE"

# Create a status file
cat > "$WORKSPACE/autonomous_status.txt" << EOL
Autonomous System Status
-----------------------
Last started: $(date '+%Y-%m-%d %H:%M:%S')
Started processes: $STARTED
Failed processes: $FAILED

Running processes:
EOL

for script in "${SCRIPTS[@]}"; do
    if is_script_running "$script"; then
        echo "• $script: Running" >> "$WORKSPACE/autonomous_status.txt"
    else
        echo "• $script: Not running" >> "$WORKSPACE/autonomous_status.txt"
    fi
done

log_message "Autonomous system startup complete"