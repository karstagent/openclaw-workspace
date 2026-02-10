#!/usr/bin/env python3

import json
import os
import sys
import datetime
import subprocess
import time
import argparse

# File paths
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
TASK_STATUS_FILE = "/Users/karst/.openclaw/workspace/current-task-status.json"
KANBAN_STATE_FILE = "/Users/karst/.openclaw/workspace/kanban-state.json"

class KanbanTaskManager:
    def __init__(self, auto_update=True):
        self.auto_update = auto_update
        self.kanban_data = self.load_kanban_data()
        self.kanban_state = self.load_kanban_state()

    def load_kanban_data(self):
        """Load the kanban board data from file"""
        try:
            with open(KANBAN_BOARD_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading kanban data: {e}")
            return {"columns": []}

    def save_kanban_data(self):
        """Save kanban board data to file"""
        try:
            # Update the lastUpdated timestamp
            self.kanban_data["lastUpdated"] = datetime.datetime.utcnow().isoformat() + "Z"
            
            with open(KANBAN_BOARD_FILE, 'w') as f:
                json.dump(self.kanban_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving kanban data: {e}")
            return False

    def load_kanban_state(self):
        """Load the kanban manager state"""
        try:
            with open(KANBAN_STATE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default state if not exists
            default_state = {
                "active_task_id": None,
                "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                "last_task_switch": datetime.datetime.utcnow().isoformat() + "Z",
                "task_history": [],
                "heartbeat_check_count": 0
            }
            self.save_kanban_state(default_state)
            return default_state

    def save_kanban_state(self, state=None):
        """Save the kanban manager state"""
        try:
            with open(KANBAN_STATE_FILE, 'w') as f:
                json.dump(state or self.kanban_state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving kanban state: {e}")
            return False

    def update_task_status(self, status_text):
        """Update the current task status display"""
        try:
            status_data = {
                "currentTaskStatus": status_text,
                "lastUpdated": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            with open(TASK_STATUS_FILE, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            print(f"Task status updated: {status_text}")
            return True
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False

    def get_in_progress_tasks(self):
        """Get all tasks in the 'in-progress' column"""
        for column in self.kanban_data.get("columns", []):
            if column.get("id") == "in-progress":
                return column.get("tasks", [])
        return []

    def get_task_by_id(self, task_id):
        """Find a task by its ID across all columns"""
        for column in self.kanban_data.get("columns", []):
            for task in column.get("tasks", []):
                if task.get("id") == task_id:
                    return task, column.get("id")
        return None, None

    def move_task(self, task_id, to_column):
        """Move a task to a different column"""
        # Find the task
        task, source_column_id = self.get_task_by_id(task_id)
        
        if not task or not source_column_id:
            print(f"Task {task_id} not found")
            return False
            
        # Find source column object and target column object
        source_column = None
        target_column = None
        
        for column in self.kanban_data.get("columns", []):
            if column.get("id") == source_column_id:
                source_column = column
            if column.get("id") == to_column:
                target_column = column
        
        if not source_column or not target_column:
            print(f"Could not find columns {source_column_id} or {to_column}")
            return False
            
        # Remove from source
        source_column["tasks"] = [t for t in source_column["tasks"] if t.get("id") != task_id]
        
        # Add to target
        if to_column == "completed":
            # Add completion date when moving to done
            task["completedDate"] = datetime.datetime.now().strftime("%Y-%m-%d")
            task["progress"] = 100
        elif to_column == "in-progress":
            # Add start date when moving to in progress
            task["startedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
        
        target_column["tasks"].append(task)
        
        # Save changes
        if self.auto_update:
            self.save_kanban_data()
            
        print(f"Moved task {task_id} from {source_column_id} to {to_column}")
        return True

    def create_task(self, title, description, priority="medium", column="backlog", **kwargs):
        """Create a new task in the specified column"""
        # Generate a task ID
        task_id = f"task-{int(datetime.datetime.now().timestamp() * 1000)}"
        
        # Create the task object
        task = {
            "id": task_id,
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
            "title": title,
            "description": description,
            "priority": priority,
            "category": kwargs.get("category", "other"),
            "assignedTo": kwargs.get("assignedTo", "Pip"),
            "assignedBy": kwargs.get("assignedBy", "Pip"),
            "dueDate": kwargs.get("dueDate", ""),
            "notes": kwargs.get("notes", ""),
            "progress": kwargs.get("progress", 0),
            "tags": kwargs.get("tags", [])
        }
        
        # Add to the column
        for col in self.kanban_data.get("columns", []):
            if col.get("id") == column:
                col["tasks"].append(task)
                break
        
        # Save the changes
        if self.auto_update:
            self.save_kanban_data()
        
        print(f"Created task {task_id}: {title}")
        return task_id

    def enforce_single_in_progress(self):
        """Ensure only one task is in the 'in-progress' column"""
        in_progress = self.get_in_progress_tasks()
        
        if len(in_progress) <= 1:
            return True  # Already compliant
        
        # Keep only the most recently started task
        newest_task = None
        newest_time = None
        
        for task in in_progress:
            started_at = task.get("startedAt")
            if started_at and (newest_time is None or started_at > newest_time):
                newest_task = task
                newest_time = started_at
        
        if not newest_task:
            # If no task has a start time, keep the first one
            newest_task = in_progress[0]
        
        # Move all other tasks back to backlog
        for task in in_progress:
            if task.get("id") != newest_task.get("id"):
                self.move_task(task.get("id"), "backlog")
                
        return True

    def update_active_task_status(self):
        """Update the task status display based on the active task"""
        in_progress = self.get_in_progress_tasks()
        
        if not in_progress:
            self.update_task_status("No task currently in progress")
            self.kanban_state["active_task_id"] = None
            return False
            
        # Use the first task in progress
        active_task = in_progress[0]
        task_id = active_task.get("id")
        
        # Update the active task in the state
        if self.kanban_state["active_task_id"] != task_id:
            self.kanban_state["active_task_id"] = task_id
            self.kanban_state["last_task_switch"] = datetime.datetime.utcnow().isoformat() + "Z"
            
            # Add to task history
            self.kanban_state["task_history"].append({
                "task_id": task_id,
                "started": self.kanban_state["last_task_switch"],
                "title": active_task.get("title")
            })
            
            # Limit history to last 20 entries
            if len(self.kanban_state["task_history"]) > 20:
                self.kanban_state["task_history"] = self.kanban_state["task_history"][-20:]
        
        # Generate status text based on task info
        progress = active_task.get("progress", 0)
        status_text = f"[{progress}%] {active_task.get('title')}"
        
        self.update_task_status(status_text)
        self.save_kanban_state()
        return True

    def heartbeat_check(self):
        """Run a kanban board check during heartbeat"""
        self.kanban_state["heartbeat_check_count"] += 1
        self.kanban_state["last_check"] = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Refresh kanban data
        self.kanban_data = self.load_kanban_data()
        
        # Enforce one task in progress
        self.enforce_single_in_progress()
        
        # Update the task status
        self.update_active_task_status()
        
        # Save state
        self.save_kanban_state()
        
        return True

def create_cron_job():
    """Set up a cron job to run the heartbeat check"""
    try:
        # Use the cron tool to create a job that runs every 5 minutes
        subprocess.run([
            "python3", 
            "/Users/karst/.openclaw/workspace/kanban-task-manager.py", 
            "--heartbeat"
        ], check=True)
        
        print("Cron job for kanban task manager has been created")
        return True
    except Exception as e:
        print(f"Error creating cron job: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Kanban Task Management System")
    parser.add_argument("--heartbeat", action="store_true", help="Run a heartbeat check")
    parser.add_argument("--create", help="Create a new task with the given title")
    parser.add_argument("--desc", help="Description for the new task")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], default="medium", help="Task priority")
    parser.add_argument("--move", help="Move a task to a different column")
    parser.add_argument("--to", choices=["backlog", "in-progress", "testing", "completed"], help="Target column")
    parser.add_argument("--enforce", action="store_true", help="Enforce one task in progress")
    parser.add_argument("--setup-cron", action="store_true", help="Set up cron job for automatic monitoring")
    
    args = parser.parse_args()
    
    manager = KanbanTaskManager()
    
    if args.heartbeat:
        manager.heartbeat_check()
    elif args.create and args.desc:
        manager.create_task(args.create, args.desc, priority=args.priority)
    elif args.move and args.to:
        manager.move_task(args.move, args.to)
    elif args.enforce:
        manager.enforce_single_in_progress()
    elif args.setup_cron:
        create_cron_job()
    else:
        # Interactive mode
        print("Kanban Task Manager")
        print("1. Show in-progress tasks")
        print("2. Create new task")
        print("3. Move task to column")
        print("4. Enforce one task in progress")
        print("5. Set up cron job")
        print("q. Quit")
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            tasks = manager.get_in_progress_tasks()
            if tasks:
                for task in tasks:
                    print(f"[{task.get('priority', 'medium').upper()}] {task.get('title')} ({task.get('progress', 0)}%)")
            else:
                print("No tasks in progress")
        elif choice == "2":
            title = input("Task title: ")
            desc = input("Task description: ")
            priority = input("Priority (low/medium/high/critical) [medium]: ") or "medium"
            manager.create_task(title, desc, priority=priority)
        elif choice == "3":
            task_id = input("Task ID: ")
            column = input("Target column (backlog/in-progress/testing/completed): ")
            manager.move_task(task_id, column)
        elif choice == "4":
            manager.enforce_single_in_progress()
        elif choice == "5":
            create_cron_job()
        elif choice.lower() == "q":
            return
        
if __name__ == "__main__":
    main()