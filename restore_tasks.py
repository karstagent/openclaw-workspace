#!/usr/bin/env python3

import json
import datetime
import time
import sys
import os

# Constants
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"
BACKUP_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json.bak"

# Core tasks to add (in sequence)
tasks = [
    {
        "title": "GlassWall Core: Create basic Express API framework",
        "description": "Set up Express.js API framework with routing structure, middleware configuration, and error handling. Implement the core API infrastructure and testing framework as specified in the architecture plan.",
        "priority": "critical",
        "category": "development",
        "dueDate": "2026-02-10",
        "sequenceNumber": 2
    },
    {
        "title": "GlassWall Core: Implement authentication system",
        "description": "Build the authentication system with JWT implementation, Twitter OAuth integration, and email-based authentication. Includes user registration, login flows, and token management as specified in the security framework.",
        "priority": "critical",
        "category": "development",
        "dueDate": "2026-02-10",
        "sequenceNumber": 3
    },
    {
        "title": "GlassWall Core: Develop message queue infrastructure",
        "description": "Implement the core message queue system with priority handling, batch processing capability, and persistence layer. Create the message handling pipeline as specified in the architecture document.",
        "priority": "critical",
        "category": "development",
        "dueDate": "2026-02-10",
        "sequenceNumber": 4
    },
    {
        "title": "GlassWall Core: Build agent room management system",
        "description": "Create the agent room management functionality including room creation, configuration, and access control. Implement the agent-specific APIs for room management as defined in the API specifications.",
        "priority": "critical",
        "category": "development",
        "dueDate": "2026-02-10",
        "sequenceNumber": 5
    }
]

# Load kanban board
with open(KANBAN_BOARD_FILE, 'r') as f:
    data = json.load(f)

# Get backlog column
backlog_column = None
for column in data['columns']:
    if column['id'] == 'backlog':
        backlog_column = column
        break

if not backlog_column:
    print("Backlog column not found!")
    sys.exit(1)

# Add tasks to backlog
tasks_added = 0
for task_data in tasks:
    # Generate task ID
    task_id = f"task-{int(time.time() * 1000) + tasks_added}"
    
    # Create task object
    task = {
        "id": task_id,
        "createdAt": datetime.datetime.now().isoformat(),
        "title": task_data["title"],
        "description": task_data["description"],
        "priority": task_data["priority"],
        "category": task_data["category"],
        "assignedTo": "Pip",
        "assignedBy": "Pip",
        "dueDate": task_data["dueDate"],
        "notes": "Part of GlassWall implementation sequence.",
        "progress": 0,
        "tags": ["glasswall", "implementation"],
        "sequenceNumber": task_data["sequenceNumber"]
    }
    
    # Add to backlog
    backlog_column["tasks"].append(task)
    print(f"Added task: {task_data['title']}")
    tasks_added += 1
    
    # Small delay to ensure unique timestamps
    time.sleep(0.01)

# Update lastUpdated
data["lastUpdated"] = datetime.datetime.now().isoformat()

# Save updated board
with open(KANBAN_BOARD_FILE, 'w') as f:
    json.dump(data, f, indent=2)
    print(f"Updated Kanban board saved")

# Move the first task to in-progress
first_task_id = None
for task in backlog_column["tasks"]:
    if task.get("sequenceNumber") == 2:  # The first task in our sequence
        first_task_id = task["id"]
        break

if first_task_id:
    command = f"python3 /Users/karst/.openclaw/workspace/kanban-task-manager.py --move {first_task_id} --to in-progress"
    print(f"Running: {command}")
    os.system(command)
    
    # Update task status
    title = "GlassWall Core: Create basic Express API framework"
    command = f'python3 /Users/karst/.openclaw/workspace/task-status-updater.py --update "[0%] {title} | Starting implementation of Express API framework"'
    print(f"Running: {command}")
    os.system(command)
else:
    print("Could not find the first task to move to in-progress")