#!/usr/bin/env python3

import json
import os
import sys
import datetime
import time
import subprocess

TASK_STATUS_FILE = "/Users/karst/.openclaw/workspace/current-task-status.json"
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"

def update_task_status(status_text):
    """Update the current task status file"""
    status_data = {
        "currentTaskStatus": status_text,
        "lastUpdated": datetime.datetime.now(datetime.UTC).isoformat()
    }
    
    with open(TASK_STATUS_FILE, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"Task status updated: {status_text}")

def get_in_progress_tasks():
    """Get all tasks currently in the 'in-progress' column"""
    try:
        with open(KANBAN_BOARD_FILE, 'r') as f:
            kanban_data = json.load(f)
        
        for column in kanban_data.get('columns', []):
            if column.get('id') == 'in-progress':
                return column.get('tasks', [])
        
        return []
    except Exception as e:
        print(f"Error reading kanban board: {e}")
        return []

def update_task_notes(task_id, notes, progress=None):
    """Update the notes and progress for a specific task"""
    try:
        with open(KANBAN_BOARD_FILE, 'r') as f:
            kanban_data = json.load(f)
        
        for column in kanban_data.get('columns', []):
            for task in column.get('tasks', []):
                if task.get('id') == task_id:
                    task['notes'] = notes
                    if progress is not None:
                        task['progress'] = progress
                    
                    kanban_data['lastUpdated'] = datetime.datetime.utcnow().isoformat() + "Z"
                    
                    with open(KANBAN_BOARD_FILE, 'w') as f:
                        json.dump(kanban_data, f, indent=2)
                    
                    print(f"Updated task {task_id} notes and progress")
                    return True
        
        print(f"Task {task_id} not found in kanban board")
        return False
    except Exception as e:
        print(f"Error updating task notes: {e}")
        return False

def print_menu(tasks):
    """Print a menu of tasks to update"""
    print("\n=== Current In-Progress Tasks ===")
    
    for i, task in enumerate(tasks, 1):
        title = task.get('title', 'Untitled Task')
        progress = task.get('progress', 0)
        priority = task.get('priority', 'normal').upper()
        
        print(f"{i}. [{priority}] {title} ({progress}% complete)")
    
    print("\nOptions:")
    print("  s - Show details for a task")
    print("  u - Update task status and notes")
    print("  p - Update progress percentage")
    print("  q - Quit")

def show_task_details(task):
    """Show detailed information about a task"""
    print("\n=== Task Details ===")
    print(f"ID: {task.get('id')}")
    print(f"Title: {task.get('title', 'Untitled')}")
    print(f"Description: {task.get('description', 'No description')}")
    print(f"Priority: {task.get('priority', 'normal').upper()}")
    print(f"Progress: {task.get('progress', 0)}%")
    print(f"Assigned To: {task.get('assignedTo', 'Unassigned')}")
    print(f"Assigned By: {task.get('assignedBy', 'Unassigned')}")
    print(f"Created: {task.get('createdAt', 'Unknown')}")
    print(f"Started: {task.get('startedAt', 'Unknown')}")
    print(f"Notes: {task.get('notes', 'No notes')}")

def main():
    """Main function to run the task status updater"""
    while True:
        # Get current in-progress tasks
        tasks = get_in_progress_tasks()
        
        if not tasks:
            print("No tasks currently in progress.")
            user_input = input("Enter a custom status or 'q' to quit: ")
            
            if user_input.lower() == 'q':
                break
            
            update_task_status(user_input)
            continue
        
        print_menu(tasks)
        user_choice = input("\nEnter your choice: ").lower()
        
        if user_choice == 'q':
            break
        elif user_choice == 's':
            task_num = int(input("Enter task number to show details: "))
            if 1 <= task_num <= len(tasks):
                show_task_details(tasks[task_num - 1])
            else:
                print("Invalid task number")
        elif user_choice == 'u':
            task_num = int(input("Enter task number to update: "))
            if 1 <= task_num <= len(tasks):
                task = tasks[task_num - 1]
                new_status = input("Enter new status text (one-line summary): ")
                new_notes = input("Enter new notes for the task: ")
                
                update_task_status(new_status)
                update_task_notes(task['id'], new_notes)
            else:
                print("Invalid task number")
        elif user_choice == 'p':
            task_num = int(input("Enter task number to update progress: "))
            if 1 <= task_num <= len(tasks):
                task = tasks[task_num - 1]
                try:
                    new_progress = int(input("Enter new progress percentage (0-100): "))
                    if 0 <= new_progress <= 100:
                        update_task_notes(task['id'], task.get('notes', ''), new_progress)
                        
                        # Also update the status to show progress
                        update_task_status(f"[{new_progress}%] {task.get('title', 'Working on task')}")
                    else:
                        print("Progress must be between 0 and 100")
                except ValueError:
                    print("Invalid progress value")
            else:
                print("Invalid task number")
        else:
            print("Invalid choice")
        
        # Wait a moment before refreshing
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Direct status update from command line
        update_task_status(" ".join(sys.argv[1:]))
    else:
        # Interactive mode
        try:
            main()
        except KeyboardInterrupt:
            print("\nExiting task status updater")