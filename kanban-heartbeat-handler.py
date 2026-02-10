#!/usr/bin/env python3

import sys
import os
import json
import subprocess
import datetime
import logging

# Set up logging
logging.basicConfig(
    filename="/Users/karst/.openclaw/workspace/logs/kanban-heartbeat.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kanban-heartbeat")

# Constants
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
TASK_STATUS_FILE = "/Users/karst/.openclaw/workspace/current-task-status.json"
KANBAN_STATE_FILE = "/Users/karst/.openclaw/workspace/kanban-state.json"

def check_kanban_state():
    """Check kanban board state and enforce rules"""
    try:
        logger.info("Starting Kanban heartbeat check")
        
        # First, verify board integrity using the integrity system
        verify_result = subprocess.run(
            ["/Users/karst/.openclaw/workspace/kanban-ops.py", "verify"],
            capture_output=True,
            text=True
        )
        
        if verify_result.returncode != 0:
            error_msg = "ALERT: Kanban board integrity check failed!"
            logger.error(error_msg)
            return error_msg
            
        logger.info("Kanban board integrity verified")
        
        # Enforce single task rule
        enforce_result = subprocess.run(
            ["/Users/karst/.openclaw/workspace/kanban-ops.py", "enforce"],
            capture_output=True,
            text=True
        )
        
        if enforce_result.returncode != 0:
            error_msg = "ALERT: Failed to enforce single task rule"
            logger.error(error_msg)
            return error_msg
            
        logger.info("Single task rule enforced")
        
        # Get current in-progress tasks count
        in_progress_count = count_in_progress_tasks()
        
        if in_progress_count == 0:
            message = "ALERT: No tasks are currently in progress. Please move a task from backlog to in-progress."
            logger.warning(message)
            return message
            
        # Generate and save a status report
        report_result = subprocess.run(
            ["/Users/karst/.openclaw/workspace/kanban-ops.py", "report"],
            capture_output=True,
            text=True
        )
        
        with open("/Users/karst/.openclaw/workspace/kanban-latest-report.md", "w") as f:
            f.write(report_result.stdout)
            
        logger.info("Status report generated and saved")
        
        # Take screenshot for verification
        try:
            screenshot_dir = "/Users/karst/.openclaw/workspace/kanban-screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_file = os.path.join(screenshot_dir, f"kanban_heartbeat_{timestamp}.png")
            
            # Try to capture screenshot if browser is available
            subprocess.run(
                ["python3", "-c", f"""
import subprocess, time
try:
    # Start browser if needed
    subprocess.run(["/Users/karst/.openclaw/workspace/ensure_mission_control_running.sh"], check=False)
    time.sleep(2)  # Give it time to start
    
    # Capture screenshot
    subprocess.run(["openclaw", "browser", "action=screenshot", 
                   "targetUrl=http://localhost:3000/dashboard/kanban", 
                   f"path={screenshot_file}", "fullPage=true"], 
                   check=True)
except Exception as e:
    print(f"Screenshot failed: {{e}}")
                """],
                check=False
            )
            
            logger.info(f"Screenshot captured: {screenshot_file}")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
        
        # Everything is good
        logger.info("Kanban heartbeat check completed successfully")
        return "HEARTBEAT_OK"
    except Exception as e:
        error_msg = f"ERROR: Kanban monitoring failed: {e}"
        logger.error(error_msg)
        return error_msg

def count_in_progress_tasks():
    """Count the number of tasks in the in-progress column"""
    try:
        with open(KANBAN_BOARD_FILE, 'r') as f:
            kanban_data = json.load(f)
        
        for column in kanban_data.get("columns", []):
            if column.get("id") == "in-progress":
                return len(column.get("tasks", []))
        return 0
    except Exception as e:
        logger.error(f"Error counting tasks: {e}")
        return 0

if __name__ == "__main__":
    # Run the check and print the result
    result = check_kanban_state()
    print(result)
    
    # Save result to a timestamped file for record-keeping
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"/Users/karst/.openclaw/workspace/logs/kanban_check_{timestamp}.log", "w") as f:
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
        f.write(f"Result: {result}\n")
    
    # Exit with appropriate code
    if result == "HEARTBEAT_OK":
        sys.exit(0)
    else:
        sys.exit(1)