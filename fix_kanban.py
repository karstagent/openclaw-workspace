#!/usr/bin/env python3

import json
import datetime
import time
import sys
import os

# Constants
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
BACKUP_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json.bak"

# Load kanban board
with open(KANBAN_BOARD_FILE, 'r') as f:
    data = json.load(f)

# Create backup
with open(BACKUP_FILE, 'w') as f:
    json.dump(data, f, indent=2)
    print(f"Created backup at {BACKUP_FILE}")

# Fix the duplicate task IDs
for column in data['columns']:
    if column['id'] == 'backlog':
        for task in column['tasks']:
            if task['title'] == "GlassWall Core: Create basic Express API framework":
                # Generate new task ID
                new_id = f"task-{int(time.time() * 1000)}"
                print(f"Updating task ID from {task['id']} to {new_id}")
                task['id'] = new_id

# Save fixed board
with open(KANBAN_BOARD_FILE, 'w') as f:
    json.dump(data, f, indent=2)
    print(f"Updated Kanban board saved")

# Now find the task with sequenceNumber = 2
next_task_id = None
next_task_title = None

for column in data['columns']:
    if column['id'] == 'backlog':
        for task in column['tasks']:
            if task.get('sequenceNumber') == 2:
                next_task_id = task['id']
                next_task_title = task['title']
                break

if next_task_id:
    print(f"\nNext task: {next_task_title}")
    print(f"Task ID: {next_task_id}")
    
    # Move the task to in-progress
    command = f"python3 /Users/karst/.openclaw/workspace/kanban-task-manager.py --move {next_task_id} --to in-progress"
    print(f"Running: {command}")
    os.system(command)
    
    # Update task status
    command = f"python3 /Users/karst/.openclaw/workspace/task-status-updater.py --update \"[0%] {next_task_title} | Starting work on Express API framework\""
    print(f"Running: {command}")
    os.system(command)
else:
    print("Could not find the next task with sequenceNumber = 2")