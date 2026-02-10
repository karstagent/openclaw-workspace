#!/bin/bash
# Autonomous Dashboard System Startup
# This script launches the entire autonomous system for 24/7 dashboard development

# Set up constants
WORKSPACE="/Users/karst/.openclaw/workspace"
AUTONOMOUS_DIR="$WORKSPACE/autonomous"
LOGS_DIR="$AUTONOMOUS_DIR/logs"

# Create necessary directories
mkdir -p "$AUTONOMOUS_DIR"
mkdir -p "$LOGS_DIR"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGS_DIR/startup.log"
}

# Check if dependencies are installed
check_dependencies() {
    log "Checking dependencies..."
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        log "ERROR: Python 3 not found"
        exit 1
    fi
    
    # Check for required packages but don't try to install them
    # We've updated the code to work without external dependencies
    log "Checking for optional packages (code will work without them)..."
    
    MISSING_PACKAGES=""
    python3 -c "import tabulate" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES tabulate"
    python3 -c "import psutil" 2>/dev/null || MISSING_PACKAGES="$MISSING_PACKAGES psutil"
    
    if [ -n "$MISSING_PACKAGES" ]; then
        log "NOTE: Some optional packages are not available: $MISSING_PACKAGES"
        log "The system will use built-in fallbacks instead."
    else
        log "All optional packages are available."
    fi
    
    log "Dependencies checked"
}

# Initialize the autonomous system
initialize_system() {
    log "Initializing autonomous system..."
    
    # Run the launcher
    python3 "$AUTONOMOUS_DIR/launch.py"
    
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to initialize autonomous system"
        exit 1
    fi
    
    log "Autonomous system initialized"
}

# Load tasks
load_tasks() {
    log "Loading dashboard tasks..."
    
    # Run the task loader
    python3 "$AUTONOMOUS_DIR/task_loader.py"
    
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to load tasks"
        exit 1
    fi
    
    log "Tasks loaded successfully"
}

# Generate initial status report
generate_status_report() {
    log "Generating initial status report..."
    
    # Run the status reporter
    python3 "$AUTONOMOUS_DIR/status_reporter.py" > "$LOGS_DIR/initial_status.txt"
    
    log "Initial status report generated"
}

# Main function
main() {
    log "Starting autonomous dashboard system..."
    
    # Check dependencies
    check_dependencies
    
    # Initialize the system
    initialize_system
    
    # Load tasks
    load_tasks
    
    # Generate initial status report
    generate_status_report
    
    log "Autonomous dashboard system started successfully"
    log "The system is now running in the background"
    log "Status reports will be generated in $AUTONOMOUS_DIR/status_report.md"
    log ""
    log "To check status: python3 $AUTONOMOUS_DIR/status_reporter.py"
    log "To add tasks:    python3 $AUTONOMOUS_DIR/task_loader.py"
    log ""
    log "Dashboard development will now continue autonomously"
}

# Run the main function
main