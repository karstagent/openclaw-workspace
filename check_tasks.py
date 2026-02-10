#!/usr/bin/env python3

import json
import sys

# Load kanban board
with open('/Users/karst/.openclaw/workspace/kanban-board.json', 'r') as f:
    data = json.load(f)

# Check each column
for column in data['columns']:
    print(f"Column: {column['id']}")
    for task in column['tasks']:
        print(f"  Task: {task['title'][:50]}... - ID: {task['id']}")

# Find next task
backlog_tasks = []
for column in data['columns']:
    if column['id'] == 'backlog':
        for task in column['tasks']:
            if 'sequenceNumber' in task:
                backlog_tasks.append(task)

if backlog_tasks:
    backlog_tasks.sort(key=lambda x: x.get('sequenceNumber', 999))
    next_task = backlog_tasks[0]
    print(f"\nNext task should be: {next_task['title']} - ID: {next_task['id']}")