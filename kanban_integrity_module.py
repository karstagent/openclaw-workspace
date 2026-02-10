#!/usr/bin/env python3

import os
import json
import hashlib
import datetime
import subprocess
import logging
import time

# Constants
KANBAN_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
INTEGRITY_LOG = "/Users/karst/.openclaw/workspace/logs/kanban-integrity.log"
TRANSACTION_LOG = "/Users/karst/.openclaw/workspace/logs/kanban-transactions.log"
SCREENSHOT_DIR = "/Users/karst/.openclaw/workspace/kanban-screenshots"
LAST_VERIFIED_HASH = "/Users/karst/.openclaw/workspace/kanban-last-verified-hash.txt"

# Ensure directories exist
os.makedirs(os.path.dirname(INTEGRITY_LOG), exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=INTEGRITY_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kanban-integrity")

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of file contents"""
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

def save_last_verified_hash(file_hash):
    """Save the last verified hash for comparison"""
    with open(LAST_VERIFIED_HASH, 'w') as f:
        f.write(file_hash)

def get_last_verified_hash():
    """Get the last verified hash"""
    if not os.path.exists(LAST_VERIFIED_HASH):
        return None
        
    with open(LAST_VERIFIED_HASH, 'r') as f:
        return f.read().strip()

def verify_board_integrity():
    """Check if the Kanban board file exists and has valid JSON"""
    try:
        if not os.path.exists(KANBAN_FILE):
            logger.error("Kanban board file does not exist!")
            return False
            
        # Check file permissions
        if not os.access(KANBAN_FILE, os.R_OK | os.W_OK):
            logger.error("Insufficient permissions on Kanban board file!")
            return False
            
        # Try to parse the JSON
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Check for required fields
        if not all(key in board_data for key in ["lastUpdated", "columns"]):
            logger.error("Missing required fields in Kanban board!")
            return False
            
        # Check column structure
        required_columns = ["backlog", "in-progress", "testing", "completed"]
        board_columns = [col["id"] for col in board_data.get("columns", [])]
        
        if not all(col in board_columns for col in required_columns):
            logger.error(f"Missing required columns! Found: {board_columns}")
            return False
        
        # Calculate and update file hash
        current_hash = calculate_file_hash(KANBAN_FILE)
        last_hash = get_last_verified_hash()
        
        if current_hash != last_hash and last_hash is not None:
            log_transaction(last_hash, current_hash, "Detected change during integrity check")
            
        save_last_verified_hash(current_hash)
        
        logger.info(f"Kanban board integrity verified: {current_hash}")
        return True
    except Exception as e:
        logger.error(f"Board integrity check failed: {e}")
        return False

def log_transaction(old_hash, new_hash, message=""):
    """Log a board transaction with before/after hashes"""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp} | {old_hash} → {new_hash} | {message}\n"
    
    with open(TRANSACTION_LOG, 'a') as f:
        f.write(log_entry)
    
    logger.info(f"Logged board transaction: {message}")

def capture_board_screenshot():
    """Capture a screenshot of the Kanban board for verification"""
    try:
        # Ensure browser is running
        subprocess.run([
            "/Users/karst/.openclaw/workspace/ensure_mission_control_running.sh"
        ], check=True)
        
        # Wait for server to be ready
        time.sleep(2)
        
        # Capture screenshot of Kanban board
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"kanban_{timestamp}.png")
        
        # Use browser tool to capture screenshot
        subprocess.run([
            "python3", "-c",
            """
import subprocess
subprocess.run(["openclaw", "browser", "action=screenshot", "targetUrl=http://localhost:3000/dashboard/kanban", f"path={screenshot_file}", "fullPage=true"], check=True)
            """
        ], shell=True)
        
        logger.info(f"Captured board screenshot: {screenshot_file}")
        return screenshot_file
    except Exception as e:
        logger.error(f"Failed to capture board screenshot: {e}")
        return None

def update_kanban_board(data):
    """Update the Kanban board with transaction logging and verification"""
    try:
        # Calculate hash of current state
        old_hash = calculate_file_hash(KANBAN_FILE)
        
        # Update lastUpdated timestamp
        data["lastUpdated"] = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Write the updated board data
        with open(KANBAN_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Calculate hash of new state
        new_hash = calculate_file_hash(KANBAN_FILE)
        
        # Log the transaction
        log_transaction(old_hash, new_hash, "Updated Kanban board")
        
        # Update the verified hash
        save_last_verified_hash(new_hash)
        
        # Capture a screenshot for visual verification
        screenshot_file = capture_board_screenshot()
        
        # Verify the board integrity after update
        is_valid = verify_board_integrity()
        
        return {
            "success": is_valid,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "screenshot": screenshot_file
        }
    except Exception as e:
        logger.error(f"Failed to update Kanban board: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def move_task(task_id, source_column, target_column):
    """Move a task between columns with transaction logging"""
    try:
        # Read current board state
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Find the task in source column
        task_to_move = None
        for column in board_data["columns"]:
            if column["id"] == source_column:
                for task in column["tasks"]:
                    if task["id"] == task_id:
                        task_to_move = task
                        column["tasks"].remove(task)
                        break
        
        if not task_to_move:
            logger.error(f"Task {task_id} not found in column {source_column}")
            return False
        
        # Add task to target column
        for column in board_data["columns"]:
            if column["id"] == target_column:
                # Update task metadata for certain columns
                if target_column == "in-progress":
                    task_to_move["startedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
                elif target_column == "completed":
                    task_to_move["completedDate"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    task_to_move["progress"] = 100
                
                # Add to target column
                column["tasks"].append(task_to_move)
                break
        
        # Update the board with transaction logging
        result = update_kanban_board(board_data)
        
        logger.info(f"Moved task {task_id} from {source_column} to {target_column}: {result['success']}")
        return result["success"]
    except Exception as e:
        logger.error(f"Failed to move task: {e}")
        return False

def update_task_progress(task_id, progress, notes=None):
    """Update task progress with transaction logging"""
    try:
        # Read current board state
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Find the task in any column
        task_found = False
        for column in board_data["columns"]:
            for task in column["tasks"]:
                if task["id"] == task_id:
                    task["progress"] = progress
                    if notes:
                        task["notes"] = notes
                    task_found = True
                    break
            if task_found:
                break
        
        if not task_found:
            logger.error(f"Task {task_id} not found in any column")
            return False
        
        # Update the board with transaction logging
        result = update_kanban_board(board_data)
        
        logger.info(f"Updated task {task_id} progress to {progress}: {result['success']}")
        return result["success"]
    except Exception as e:
        logger.error(f"Failed to update task progress: {e}")
        return False

def enforce_single_task_in_progress():
    """Ensure only one task is in the in-progress column"""
    try:
        # Read current board state
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Find in-progress column
        in_progress_tasks = []
        for column in board_data["columns"]:
            if column["id"] == "in-progress":
                in_progress_tasks = column["tasks"]
                break
        
        # If no issues, just return
        if len(in_progress_tasks) <= 1:
            logger.info("Single task rule already satisfied")
            return True
        
        # Find the most recently started task
        most_recent = None
        most_recent_time = None
        
        for task in in_progress_tasks:
            started_at = task.get("startedAt")
            if started_at and (most_recent_time is None or started_at > most_recent_time):
                most_recent = task
                most_recent_time = started_at
        
        # If no task has a start time, keep the first one
        if not most_recent:
            most_recent = in_progress_tasks[0]
        
        # Update board to keep only one task
        for column in board_data["columns"]:
            if column["id"] == "in-progress":
                column["tasks"] = [most_recent]
                break
        
        # Update the board with transaction logging
        result = update_kanban_board(board_data)
        
        logger.info(f"Enforced single task rule, kept {most_recent['id']}: {result['success']}")
        return result["success"]
    except Exception as e:
        logger.error(f"Failed to enforce single task rule: {e}")
        return False

def get_current_in_progress_task():
    """Get the currently in-progress task"""
    try:
        # Read current board state
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Find in-progress column
        for column in board_data["columns"]:
            if column["id"] == "in-progress":
                if column["tasks"]:
                    return column["tasks"][0]
                break
        
        return None
    except Exception as e:
        logger.error(f"Failed to get in-progress task: {e}")
        return None

def generate_status_report():
    """Generate a status report with integrity check"""
    try:
        # Verify board integrity first
        if not verify_board_integrity():
            return "ERROR: Kanban board integrity check failed"
        
        # Read current board state
        with open(KANBAN_FILE, 'r') as f:
            board_data = json.load(f)
        
        # Get tasks by column
        column_tasks = {}
        for column in board_data["columns"]:
            column_tasks[column["id"]] = column["tasks"]
        
        # Build report
        report = ["# Kanban Board Status Report"]
        report.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Add board hash for verification
        board_hash = calculate_file_hash(KANBAN_FILE)
        report.append(f"Board Hash: {board_hash}")
        
        # In Progress section
        report.append("\n## 🔄 In Progress")
        if column_tasks.get("in-progress"):
            for task in column_tasks["in-progress"]:
                progress = task.get('progress', 50)
                report.append(f"- {task['title']} ({progress}% complete)")
                report.append(f"  - Notes: {task.get('notes', 'No notes')}")
        else:
            report.append("- No tasks currently in progress")
        
        # Review section
        report.append("\n## 👀 In Review")
        if column_tasks.get("testing"):
            for task in column_tasks["testing"]:
                progress = task.get('progress', 90)
                report.append(f"- {task['title']} ({progress}% complete)")
                report.append(f"  - Notes: {task.get('notes', 'No notes')}")
        else:
            report.append("- No tasks in review")
        
        # Done section
        report.append("\n## ✅ Completed")
        if column_tasks.get("completed"):
            for task in column_tasks["completed"]:
                report.append(f"- {task['title']}")
        else:
            report.append("- No completed tasks")
        
        # Backlog section
        report.append("\n## 📋 Backlog")
        if column_tasks.get("backlog"):
            for task in column_tasks["backlog"]:
                progress = task.get('progress', 0)
                report.append(f"- {task['title']} ({progress}% complete)")
        else:
            report.append("- No tasks in backlog")
        
        # Take a screenshot for verification
        screenshot_file = capture_board_screenshot()
        if screenshot_file:
            report.append(f"\nVerification Screenshot: {screenshot_file}")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Failed to generate status report: {e}")
        return f"ERROR: Failed to generate status report: {e}"