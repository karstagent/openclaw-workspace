# Task Review Process

## Overview
This document outlines the standardized process for reviewing tasks in the Mission Control system. The review process ensures quality control, proper documentation, and integration with the Kanban board workflow.

## Review Workflow

### 1. Task Completion
When a task is completed, it should be moved to the "Review" column in the Kanban board with:
- Progress set to 100%
- Comprehensive notes on implementation
- All required deliverables available for review

### 2. Review Initiation
A review is initiated by:
- Running `python3 /Users/karst/.openclaw/workspace/task-review.py create --task-id <task-id>`
- This creates a review template in the task-reviews directory
- The review is assigned to the task's assignedBy person by default

### 3. Review Process
The reviewer should:
- Examine all code, documentation, and deliverables
- Test functionality if applicable
- Complete the review template with comments and findings
- Make a decision: Approve, Request Changes, or Reject

### 4. Review Completion
To complete a review:
- Run `python3 /Users/karst/.openclaw/workspace/task-review.py complete --review-file <review-file> --decision <approve|change|reject>`
- This moves the task to the appropriate column based on the decision
- The Kanban board is updated with the review metadata

### 5. Review Decisions

#### Approve
- Task is moved to the "Done" column
- Completion date is recorded
- All review metadata is attached to the task

#### Request Changes
- Task is moved back to the "In Progress" column
- Review comments are added to the task notes
- Task progress is adjusted to reflect needed changes

#### Reject
- Task is moved to the "To Do" column
- Review comments are added to the task notes
- Task progress is reset to 0%

## Review Metadata
Each review captures:
- Reviewer identity
- Review date and time
- Decision and reasoning
- Action items (if any)
- Transaction verification (integrity hash)

## Integration with Kanban System
The review process:
- Maintains transaction integrity through the kanban-integrity system
- Updates the task status banner with review information
- Properly documents the review history
- Ensures consistent state across the entire system