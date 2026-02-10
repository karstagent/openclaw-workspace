# Kanban Board Real-Time Integrity System

This system ensures that the Kanban board is always updated in real time, with multiple layers of verification and integrity checks.

## Components

### 1. Core Integrity System (`kanban-integrity.py`)

The foundation of the system, providing:

- Hash-based transaction verification
- Board structure validation
- Screenshot capture for visual verification
- Transaction logging with before/after states
- Task movement with proper metadata updates
- Progress tracking with verification

### 2. Operations API (`kanban-ops.py`)

A command-line interface for all Kanban operations:

```bash
# Verify board integrity
./kanban-ops.py verify

# Create a new task
./kanban-ops.py create --title "Task title" --desc "Description" --priority high

# Move a task between columns
./kanban-ops.py move --task-id task-123456 --from backlog --to in-progress

# Update task progress
./kanban-ops.py update --task-id task-123456 --progress 75 --notes "Making good progress"

# Enforce single task rule
./kanban-ops.py enforce

# Generate status report
./kanban-ops.py report
```

### 3. Automated Verification (`verify_kanban_integrity.sh`)

Runs every 3 minutes to:

- Verify board structure and integrity
- Check for unauthorized changes
- Validate hash consistency
- Log all verification results
- Send alerts on integrity failures
- Attempt auto-recovery when possible

### 4. Heartbeat Integration (`kanban-heartbeat-handler.py`)

Runs every 15 minutes to:

- Enforce the single-task rule
- Generate comprehensive status reports
- Capture verification screenshots
- Produce detailed logs of all board operations
- Validate the integrity of all board operations
- Ensure task status display is accurate

## Key Features

### 1. Transaction Logging

Every change to the Kanban board is logged with:

- Before and after state hashes
- Timestamp of the change
- Description of the operation
- Visual verification (screenshots)

### 2. Integrity Verification

The board is continually verified for:

- Structure validity (required columns exist)
- JSON validity
- File permissions
- Content consistency
- Transaction integrity

### 3. Rule Enforcement

The system automatically enforces:

- Single task in progress rule
- Proper task metadata (completion dates, progress values)
- Correct column structure
- Valid state transitions

### 4. Visual Verification

- Screenshots are captured after every significant change
- Screenshots are stored in `/Users/karst/.openclaw/workspace/kanban-screenshots/`
- Screenshots are timestamped for audit purposes

## Logs and Reports

All system activities are logged in:

- `/Users/karst/.openclaw/workspace/logs/kanban-integrity.log` - Integrity checks
- `/Users/karst/.openclaw/workspace/logs/kanban-transactions.log` - Board changes
- `/Users/karst/.openclaw/workspace/logs/kanban-verification.log` - 3-minute verifications
- `/Users/karst/.openclaw/workspace/logs/kanban-heartbeat.log` - 15-minute heartbeats
- `/Users/karst/.openclaw/workspace/logs/kanban_check_*.log` - Individual check results

## Integration with Cron

Two cron jobs are set up:

1. Integrity verification every 3 minutes
2. Heartbeat checks every 15 minutes

This ensures continuous monitoring and verification of the board state.

## Usage

Use the `kanban-ops.py` script for all Kanban operations to ensure proper tracking and verification. Never modify the JSON file directly.

## Verification Status

The latest verification status is always available in:
`/Users/karst/.openclaw/workspace/kanban-latest-report.md`

This report is updated during every heartbeat check and includes:
- Current board state
- Integrity verification result
- Link to the latest verification screenshot