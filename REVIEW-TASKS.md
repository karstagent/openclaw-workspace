# Task Review System Documentation

## Overview

The Task Review System provides a structured approach for reviewing completed tasks before they are marked as done. This ensures quality control, proper documentation, and maintains the integrity of the Kanban workflow.

## Key Features

### Automated Review Template Generation
- Creates standardized review templates for each task
- Populates templates with task metadata and implementation details
- Stores reviews in a centralized location for reference

### Review Decision Workflow
- Supports three decision paths: Approve, Request Changes, Reject
- Automatically moves tasks to appropriate columns based on review decisions
- Maintains review history and metadata with each task

### Integration with Kanban System
- Uses transaction verification to ensure data integrity
- Updates task status and progress based on review outcomes
- Tracks review metrics for process improvement

## Command Reference

### Create a Review
```bash
python3 task-review.py create --task-id <task-id> [--reviewer <name>]
```

### Complete a Review
```bash
python3 task-review.py complete --review-file <path> --decision <approve|change|reject> [--comments <text>]
```

### List Pending Reviews
```bash
python3 task-review.py list
```

### Check Review Status
```bash
python3 task-review.py status --task-id <task-id>
```

## Review Process

1. **Task Completion**:
   - Developer completes task and moves it to the Review column
   - Progress should be set to 100% with comprehensive implementation notes

2. **Review Initiation**:
   - Reviewer or system creates a review template
   - Task metadata is automatically included in the template

3. **Review Evaluation**:
   - Reviewer examines the implementation against requirements
   - Tests functionality if applicable
   - Documents findings in the review template

4. **Decision Making**:
   - Reviewer makes a decision: Approve, Request Changes, or Reject
   - Provides reasoning and any necessary action items

5. **Process Completion**:
   - System updates Kanban board based on the decision
   - Task moves to appropriate column with updated metadata
   - Review is archived for future reference

## Implementation Architecture

The review system is built on several components:

- **task-review.py**: Main script handling review operations
- **task-reviews/**: Directory containing review templates and completed reviews
- **kanban-integrity-module.py**: Ensures data integrity during review transactions
- **review-templates/**: Contains template formats for different review types

## Integration Points

- **Kanban Board**: Directly interfaces with the Kanban JSON structure
- **Task Status**: Updates the current task status during review operations
- **Metadata System**: Records review history in task metadata