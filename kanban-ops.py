#!/usr/bin/env python3

import sys
import argparse
import json
import datetime
import os

# Add the current directory to the path to make imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the kanban-integrity.py file directly
# Avoid using the symlink (kanban_integrity.py) which causes circular imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kanban_integrity_module import (
    verify_board_integrity, 
    update_task_progress,
    move_task, 
    enforce_single_task_in_progress,
    generate_status_report
)

def create_task(title, description, priority="medium", column="backlog", **kwargs):
    """Create a new task in the specified column"""
    try:
        from kanban_integrity_module import update_kanban_board
        
        # Read current board
        with open("/Users/karst/.openclaw/workspace/kanban-board.json", 'r') as f:
            board_data = json.load(f)
        
        # Generate task ID
        task_id = f"task-{int(datetime.datetime.now().timestamp() * 1000)}"
        
        # Create task object
        task = {
            "id": task_id,
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
            "title": title,
            "description": description,
            "priority": priority,
            "category": kwargs.get("category", "other"),
            "assignedTo": kwargs.get("assignedTo", "Pip"),
            "assignedBy": kwargs.get("assignedBy", "Jordan"),
            "dueDate": kwargs.get("dueDate", ""),
            "notes": kwargs.get("notes", ""),
            "progress": kwargs.get("progress", 0),
            "tags": kwargs.get("tags", [])
        }
        
        # Add to the target column
        found_column = False
        for col in board_data["columns"]:
            if col["id"] == column:
                col["tasks"].append(task)
                found_column = True
                break
                
        if not found_column:
            print(f"Error: Column {column} not found")
            return False
        
        # Update board with transaction tracking
        result = update_kanban_board(board_data)
        
        if result["success"]:
            print(f"Created task {task_id}: {title}")
            
            # Send notification
            if column == "in-progress":
                enforce_single_task_in_progress()
            
            return task_id
        else:
            print(f"Error creating task: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Error creating task: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Kanban Board Operations")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Verify integrity command
    verify_parser = subparsers.add_parser("verify", help="Verify board integrity")
    
    # Create task command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument("--desc", required=True, help="Task description")
    create_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], default="medium", help="Task priority")
    create_parser.add_argument("--column", choices=["backlog", "in-progress", "testing", "completed"], default="backlog", help="Target column")
    
    # Move task command
    move_parser = subparsers.add_parser("move", help="Move a task")
    move_parser.add_argument("--task-id", required=True, help="Task ID to move")
    move_parser.add_argument("--from", dest="source", required=True, choices=["backlog", "in-progress", "testing", "completed"], help="Source column")
    move_parser.add_argument("--to", dest="target", required=True, choices=["backlog", "in-progress", "testing", "completed"], help="Target column")
    
    # Update task command
    update_parser = subparsers.add_parser("update", help="Update task progress")
    update_parser.add_argument("--task-id", required=True, help="Task ID to update")
    update_parser.add_argument("--progress", required=True, type=int, help="New progress value (0-100)")
    update_parser.add_argument("--notes", help="Updated task notes")
    
    # Enforce command
    enforce_parser = subparsers.add_parser("enforce", help="Enforce single task rule")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate status report")
    
    args = parser.parse_args()
    
    if args.command == "verify":
        if verify_board_integrity():
            print("Kanban board integrity verified.")
            return 0
        else:
            print("ERROR: Kanban board integrity check failed!")
            return 1
    
    elif args.command == "create":
        task_id = create_task(args.title, args.desc, args.priority, args.column)
        if task_id:
            print(f"Task created with ID: {task_id}")
            return 0
        else:
            return 1
    
    elif args.command == "move":
        if move_task(args.task_id, args.source, args.target):
            print(f"Moved task {args.task_id} from {args.source} to {args.target}")
            return 0
        else:
            print(f"Failed to move task {args.task_id}")
            return 1
    
    elif args.command == "update":
        if update_task_progress(args.task_id, args.progress, args.notes):
            print(f"Updated task {args.task_id} progress to {args.progress}%")
            return 0
        else:
            print(f"Failed to update task {args.task_id}")
            return 1
    
    elif args.command == "enforce":
        if enforce_single_task_in_progress():
            print("Single task rule enforced")
            return 0
        else:
            print("Failed to enforce single task rule")
            return 1
    
    elif args.command == "report":
        report = generate_status_report()
        print(report)
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())