#!/usr/bin/env python3

import json
import datetime
import sys

# Constants
KANBAN_BOARD_FILE = "/Users/karst/.openclaw/workspace/kanban-board.json"

def update_task(task_id, progress, notes):
    # Load current kanban board
    with open(KANBAN_BOARD_FILE, "r") as f:
        data = json.load(f)
    
    # Find and update the task
    found = False
    for column in data["columns"]:
        for task in column["tasks"]:
            if task["id"] == task_id:
                task["progress"] = progress
                task["notes"] = notes
                found = True
                print(f"Updated task {task_id} to {progress}% complete")
                break
        if found:
            break
    
    if not found:
        print(f"Task {task_id} not found in any column")
        return False
    
    # Update lastUpdated timestamp
    data["lastUpdated"] = datetime.datetime.now().isoformat()
    
    # Save changes
    with open(KANBAN_BOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved updates to Kanban board")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 update-kanban-task.py <task_id> <progress> <notes>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    progress = int(sys.argv[2])
    notes = sys.argv[3]
    
    update_task(task_id, progress, notes)