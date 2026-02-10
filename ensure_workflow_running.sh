#!/bin/bash
# Script to ensure the development workflow stays running

WORKFLOW_SCRIPT="/Users/karst/.openclaw/workspace/dev_workflow.py"
WORKFLOW_PID_FILE="/Users/karst/.openclaw/workspace/dev_workflow.pid"
LOG_FILE="/Users/karst/.openclaw/workspace/ensure_workflow.log"
DEV_WORKFLOW_LOG="/Users/karst/.openclaw/workspace/dev_workflow.log"

# Function to log messages
log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if workflow completed normally (this is a good state)
check_if_completed_normally() {
  if [ -f "$DEV_WORKFLOW_LOG" ]; then
    if tail -1 "$DEV_WORKFLOW_LOG" | grep -q "Development workflow completed"; then
      LAST_MODIFIED=$(stat -f "%m" "$DEV_WORKFLOW_LOG")
      CURRENT_TIME=$(date +%s)
      DIFFERENCE=$(($CURRENT_TIME - $LAST_MODIFIED))
      
      # If the log was updated in the last minute, it completed normally
      if [ $DIFFERENCE -lt 60 ]; then
        return 0  # Completed normally
      fi
    fi
  fi
  return 1  # Did not complete normally
}

# Run the workflow once
run_workflow_once() {
  log_message "Running workflow once"
  python3 "$WORKFLOW_SCRIPT" > /Users/karst/.openclaw/workspace/dev_workflow.out 2>&1
  log_message "Workflow execution completed"
}

# Check if workflow needs to be run on schedule
check_schedule() {
  LAST_RUN_TIME=$(stat -f "%m" "$DEV_WORKFLOW_LOG" 2>/dev/null || echo 0)
  CURRENT_TIME=$(date +%s)
  DIFFERENCE=$(($CURRENT_TIME - $LAST_RUN_TIME))
  
  # Run every 7 minutes (420 seconds)
  if [ $DIFFERENCE -gt 420 ]; then
    log_message "It's been $DIFFERENCE seconds since last run, running workflow on schedule"
    run_workflow_once
    return 0
  fi
  
  log_message "Workflow ran $DIFFERENCE seconds ago, no need to run again yet"
  return 1
}

# Main logic
if check_if_completed_normally; then
  log_message "Workflow completed normally, checking schedule for next run"
  check_schedule
else
  log_message "Workflow did not complete normally, running it now"
  run_workflow_once
fi

# Remove the PID file since we're running synchronously now
if [ -f "$WORKFLOW_PID_FILE" ]; then
  rm "$WORKFLOW_PID_FILE"
fi

# Schedule the script to run again in 7 minutes via cron
# But first check if it's already in crontab to avoid duplicates
CRON_ENTRY="*/7 * * * * /Users/karst/.openclaw/workspace/ensure_workflow_running.sh"
if ! (crontab -l 2>/dev/null | grep -q "$CRON_ENTRY"); then
  (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | sort | uniq | crontab -
  log_message "Added cron entry for workflow monitoring"
fi