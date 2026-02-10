#!/usr/bin/env python3

import sys
import os
import json
import argparse
import datetime
import subprocess

# Add the current directory to the path to make imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Constants
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
REVIEW_DIR = "/Users/karst/.openclaw/workspace/task-reviews"

def load_kanban_board():
    """Load the Kanban board data"""
    try:
        with open(KANBAN_BOARD_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Kanban board: {e}")
        return None

def save_kanban_board(data):
    """Save the Kanban board data with proper timestamps"""
    try:
        # Update lastUpdated timestamp
        data["lastUpdated"] = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Write to file
        with open(KANBAN_BOARD_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Kanban board updated successfully")
        
        # Use the kanban-integrity system to log this change properly
        try:
            subprocess.run(
                ["/Users/karst/.openclaw/workspace/kanban-integrity.py"],
                check=True
            )
        except Exception as e:
            print(f"Warning: Could not run integrity check: {e}")
            
        return True
    except Exception as e:
        print(f"Error saving Kanban board: {e}")
        return False

def get_review_tasks():
    """Get all tasks in the review column"""
    board_data = load_kanban_board()
    
    if not board_data:
        return []
        
    for column in board_data.get("columns", []):
        if column.get("id") == "testing":
            return column.get("tasks", [])
            
    return []

def generate_review_file(task):
    """Generate a review file for a task"""
    # Create review directory if it doesn't exist
    os.makedirs(REVIEW_DIR, exist_ok=True)
    
    # Create a filename based on task ID
    filename = os.path.join(REVIEW_DIR, f"{task['id']}-review.md")
    
    # Build the review content
    lines = [
        f"# Task Review: {task['title']}",
        "",
        "## Task Details",
        f"- **ID**: {task.get('id', 'Unknown')}",
        f"- **Priority**: {task.get('priority', 'medium').upper()}",
        f"- **Assigned To**: {task.get('assignedTo', 'Unassigned')}",
        f"- **Created**: {task.get('createdAt', 'Unknown')}",
        f"- **Progress**: {task.get('progress', 0)}%",
        "",
        "## Description",
        f"{task.get('description', 'No description provided.')}",
        "",
        "## Implementation Notes",
        f"{task.get('notes', 'No implementation notes provided.')}",
        "",
        "## Review Decision",
        "Please review the task implementation and make your decision:",
        "",
        f"1. **Approve**: Move to Completed column",
        f"   - Run: `./task-review.py approve {task['id']}`",
        "",
        f"2. **Request Changes**: Keep in Review column with feedback",
        f"   - Run: `./task-review.py request-changes {task['id']} \"Your feedback here\"`",
        "",
        f"3. **Reject**: Move back to Backlog column",
        f"   - Run: `./task-review.py reject {task['id']} \"Reason for rejection\"`",
        "",
        "## Review Notes",
        "_Add your review notes here for future reference_",
        ""
    ]
    
    # Write the review file
    with open(filename, 'w') as f:
        f.write("\n".join(lines))
        
    print(f"Review file generated: {filename}")
    return filename

def list_reviews():
    """List all tasks in the review column with options"""
    review_tasks = get_review_tasks()
    
    if not review_tasks:
        print("No tasks currently in review.")
        return
    
    print("Tasks in Review:")
    print("================")
    
    for i, task in enumerate(review_tasks, 1):
        print(f"{i}. [{task.get('priority', 'medium').upper()}] {task['title']} ({task.get('progress', 0)}%)")
        print(f"   ID: {task['id']}")
        print(f"   Assigned to: {task.get('assignedTo', 'Unassigned')}")
        print("   Options:")
        print(f"   - Review: ./task-review.py review {task['id']}")
        print(f"   - Approve: ./task-review.py approve {task['id']}")
        print(f"   - Request Changes: ./task-review.py request-changes {task['id']} \"Feedback...\"")
        print(f"   - Reject: ./task-review.py reject {task['id']} \"Reason...\"")
        print()

def create_review(task_id):
    """Create a review file for a specific task"""
    review_tasks = get_review_tasks()
    
    for task in review_tasks:
        if task["id"] == task_id:
            review_file = generate_review_file(task)
            
            # Open the review file in the default editor
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", review_file], check=True)
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", review_file], check=True)
                elif sys.platform == "win32":
                    subprocess.run(["start", review_file], shell=True, check=True)
                else:
                    print(f"Review file created: {review_file}")
                    print("Please open it manually.")
                    
                return True
            except Exception as e:
                print(f"Error opening review file: {e}")
                print(f"Review file created: {review_file}")
                print("Please open it manually.")
                return True
    
    print(f"Task with ID {task_id} not found in review column.")
    return False

def approve_task(task_id):
    """Approve a task and move it to completed column"""
    board_data = load_kanban_board()
    
    if not board_data:
        return False
    
    # Find the task in the review column
    task_to_move = None
    testing_column = None
    
    for column in board_data["columns"]:
        if column["id"] == "testing":
            testing_column = column
            for task in column["tasks"]:
                if task["id"] == task_id:
                    task_to_move = task
                    column["tasks"].remove(task)
                    break
            break
    
    if not task_to_move:
        print(f"Task {task_id} not found in review column.")
        return False
    
    # Add task to completed column
    for column in board_data["columns"]:
        if column["id"] == "completed":
            # Update task metadata
            task_to_move["completedDate"] = datetime.datetime.now().strftime("%Y-%m-%d")
            task_to_move["progress"] = 100
            
            # Add approval metadata
            task_to_move["reviewedBy"] = "Jordan"
            task_to_move["reviewedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
            task_to_move["reviewResult"] = "approved"
            
            # Add to completed column
            column["tasks"].append(task_to_move)
            break
    
    # Save Kanban board
    if save_kanban_board(board_data):
        print(f"Task {task_id} approved and moved to completed column.")
        return True
    
    # If save failed, restore task to review column
    if testing_column:
        testing_column["tasks"].append(task_to_move)
        save_kanban_board(board_data)
        
    return False

def request_changes(task_id, feedback):
    """Request changes for a task with feedback"""
    board_data = load_kanban_board()
    
    if not board_data:
        return False
    
    # Find the task in the review column
    task_to_update = None
    
    for column in board_data["columns"]:
        if column["id"] == "testing":
            for task in column["tasks"]:
                if task["id"] == task_id:
                    task_to_update = task
                    
                    # Add review feedback
                    task["reviewFeedback"] = feedback
                    task["reviewedBy"] = "Jordan"
                    task["reviewedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
                    task["reviewResult"] = "changes-requested"
                    
                    break
            break
    
    if not task_to_update:
        print(f"Task {task_id} not found in review column.")
        return False
    
    # Save Kanban board
    if save_kanban_board(board_data):
        print(f"Feedback provided for task {task_id}. Task remains in review column.")
        return True
        
    return False

def reject_task(task_id, reason):
    """Reject a task and move it back to backlog"""
    board_data = load_kanban_board()
    
    if not board_data:
        return False
    
    # Find the task in the review column
    task_to_move = None
    testing_column = None
    
    for column in board_data["columns"]:
        if column["id"] == "testing":
            testing_column = column
            for task in column["tasks"]:
                if task["id"] == task_id:
                    task_to_move = task
                    column["tasks"].remove(task)
                    break
            break
    
    if not task_to_move:
        print(f"Task {task_id} not found in review column.")
        return False
    
    # Add task to backlog column
    for column in board_data["columns"]:
        if column["id"] == "backlog":
            # Update task metadata
            task_to_move["rejectionReason"] = reason
            task_to_move["reviewedBy"] = "Jordan"
            task_to_move["reviewedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
            task_to_move["reviewResult"] = "rejected"
            
            # Adjust progress based on feedback
            # Don't set to 0, but reduce to show it needs more work
            current_progress = task_to_move.get("progress", 0)
            task_to_move["progress"] = max(current_progress // 2, 25)
            
            # Add to backlog column
            column["tasks"].append(task_to_move)
            break
    
    # Save Kanban board
    if save_kanban_board(board_data):
        print(f"Task {task_id} rejected and moved back to backlog.")
        return True
    
    # If save failed, restore task to review column
    if testing_column:
        testing_column["tasks"].append(task_to_move)
        save_kanban_board(board_data)
        
    return False

def main():
    parser = argparse.ArgumentParser(description="Kanban Task Review System")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks in review")
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Create a review for a task")
    review_parser.add_argument("task_id", help="Task ID to review")
    
    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve a task")
    approve_parser.add_argument("task_id", help="Task ID to approve")
    
    # Request changes command
    request_parser = subparsers.add_parser("request-changes", help="Request changes for a task")
    request_parser.add_argument("task_id", help="Task ID to request changes for")
    request_parser.add_argument("feedback", help="Feedback for requested changes")
    
    # Reject command
    reject_parser = subparsers.add_parser("reject", help="Reject a task")
    reject_parser.add_argument("task_id", help="Task ID to reject")
    reject_parser.add_argument("reason", help="Reason for rejection")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_reviews()
    elif args.command == "review":
        create_review(args.task_id)
    elif args.command == "approve":
        approve_task(args.task_id)
    elif args.command == "request-changes":
        request_changes(args.task_id, args.feedback)
    elif args.command == "reject":
        reject_task(args.task_id, args.reason)
    else:
        list_reviews()
    
if __name__ == "__main__":
    main()