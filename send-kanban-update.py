#!/usr/bin/env python3

import os
import json
import datetime
import subprocess

# File paths
KANBAN_FILE = '/Users/karst/.openclaw/workspace/kanban-board.json'
MESSAGE_FILE = '/Users/karst/.openclaw/workspace/kanban-update-message.txt'

def get_in_progress_task():
    """Get information about the current in-progress task"""
    try:
        with open(KANBAN_FILE, 'r') as f:
            data = json.load(f)
        
        for column in data.get('columns', []):
            if column.get('id') == 'in-progress':
                tasks = column.get('tasks', [])
                if tasks:
                    task = tasks[0]  # Get the first task
                    return f"Current task: {task.get('title')} ({task.get('progress', 0)}% complete)"
        
        return "No task currently in progress."
    except Exception as e:
        print(f"Error reading Kanban board: {e}")
        return "Error reading current task information."

def main():
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get in-progress task info
    task_info = get_in_progress_task()
    
    # Create the update message
    message = f"🔄 AUTOMATED KANBAN UPDATE ({timestamp}):\n{task_info}\nNext update in 5 minutes."
    
    # Save the message to a file
    with open(MESSAGE_FILE, 'w') as f:
        f.write(message)
    
    print(message)
    return message

if __name__ == "__main__":
    main()