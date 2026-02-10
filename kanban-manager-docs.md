# Kanban Task Management System

## Overview

The Kanban Task Management System enforces proper usage of the Kanban board methodology for tracking work. It integrates with the heartbeat system to ensure continuous monitoring and enforcement of Kanban discipline.

## Key Features

1. **Single-Task Focus**: Enforces only one task in the "In Progress" column at a time
2. **Real-time Task Status**: Updates the task status banner with current task information
3. **Automated Card Movement**: Validates and enforces card movement between columns
4. **Heartbeat Integration**: Regularly checks Kanban board state during heartbeat cycles
5. **Task History Tracking**: Maintains history of task switches and durations

## Components

### 1. Kanban Task Manager (`kanban-task-manager.py`)

The core component that handles all Kanban board operations:

- Moving tasks between columns
- Enforcing single-task focus
- Creating new tasks
- Updating task status
- Maintaining task history

**Usage:**
```bash
# Run a heartbeat check
./kanban-task-manager.py --heartbeat

# Create a new task
./kanban-task-manager.py --create "Task title" --desc "Description" --priority high

# Move a task between columns
./kanban-task-manager.py --move "task-id" --to "in-progress"

# Enforce single-task focus
./kanban-task-manager.py --enforce
```

### 2. Kanban Heartbeat Handler (`kanban-heartbeat-handler.py`)

Integrates with the OpenClaw heartbeat system:

- Runs during heartbeat checks
- Validates Kanban board state
- Reports issues or confirms correct usage
- Automatically enforces rules

**Usage:**
```bash
# Run directly
./kanban-heartbeat-handler.py
```

### 3. Task Status Updater (`task-status-updater.py`)

Updates the task status displayed on the Mission Control dashboard:

- Updates the current task status
- Can be run manually or by the Kanban manager
- Provides interactive or command-line interface

**Usage:**
```bash
# Update status directly
./task-status-updater.py "Working on feature X"

# Interactive mode
./task-status-updater.py
```

## Heartbeat Integration

The Kanban management system is integrated with the heartbeat system:

1. Heartbeat checks run every 15 minutes to validate Kanban state
2. Enforces single-task focus automatically
3. Updates task status based on current in-progress task
4. Reports issues when rules are violated

## Cron Jobs

The following cron jobs are set up to maintain the system:

1. Kanban heartbeat check every 15 minutes
2. Heartbeat runner every 5 minutes (which includes Kanban checks)

## Workflow Guidelines

1. Create a card for each new task
2. Move only one card to "In Progress" at a time
3. Complete or pause the current task before starting a new one
4. Move completed tasks to "Review" for feedback or "Done" when finished
5. Move paused tasks back to "To Do" with notes on progress

## File Locations

- **Kanban Board**: `/Users/karst/.openclaw/workspace/kanban-board.json`
- **Task Status**: `/Users/karst/.openclaw/workspace/current-task-status.json`
- **Kanban State**: `/Users/karst/.openclaw/workspace/kanban-state.json`
- **Log Files**: `/Users/karst/.openclaw/workspace/logs/`