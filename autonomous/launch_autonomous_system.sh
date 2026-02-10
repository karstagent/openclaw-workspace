#!/bin/bash
# Unified Autonomous System Launch Script for OpenClaw
# This script starts all the autonomous systems needed for full automation

# Constants
WORKSPACE="/Users/karst/.openclaw/workspace"
AUTONOMOUS_DIR="$WORKSPACE/autonomous"
LOGS_DIR="$WORKSPACE/logs"
MEMORY_DIR="$WORKSPACE/memory"

# Ensure directories exist
mkdir -p "$LOGS_DIR"
mkdir -p "$MEMORY_DIR"
mkdir -p "$WORKSPACE/autonomous_messages"

# Timestamp function
timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Log function
log() {
    echo "$(timestamp) - $1" | tee -a "$LOGS_DIR/autonomous_launch.log"
}

# Setup cron jobs if needed
setup_cron_jobs() {
    log "Setting up cron jobs..."
    python3 "$AUTONOMOUS_DIR/cron_job_manager.py" setup
    log "Cron jobs setup complete"
}

# Ensure API health monitoring is running
start_api_monitoring() {
    log "Starting API health monitoring..."
    python3 "$AUTONOMOUS_DIR/api_health_monitor.py"
    
    # Schedule regular checks via cron
    log "API health monitoring started"
}

# Prepare today's memory file
prepare_memory() {
    log "Preparing memory system..."
    python3 "$AUTONOMOUS_DIR/memory_manager.py"
    log "Memory system prepared"
}

# Run the heartbeat system once to initialize it
initialize_heartbeat() {
    log "Initializing heartbeat system..."
    python3 "$AUTONOMOUS_DIR/heartbeat_runner.py"
    log "Heartbeat initialization complete"
}

# Main function
main() {
    log "Starting unified autonomous system..."
    
    # Prepare memory system
    prepare_memory
    
    # Run API health monitoring
    start_api_monitoring
    
    # Set up cron jobs
    setup_cron_jobs
    
    # Initialize heartbeat
    initialize_heartbeat
    
    log "All autonomous systems started successfully"
    
    # Provide instructions for manual control
    echo ""
    echo "==================================="
    echo "Autonomous System Ready"
    echo "==================================="
    echo ""
    echo "To check status: cat $WORKSPACE/autonomous_status.txt"
    echo "To view logs: cat $LOGS_DIR/heartbeat_runner.log"
    echo "To send a message: python3 $WORKSPACE/send_message.py \"Your message\""
    echo ""
    echo "Cron jobs have been configured for regular checks"
    echo "Memory system is prepared and will update automatically"
    echo ""
    echo "The system is now fully autonomous!"
    echo "==================================="
}

# Run the main function
main