# Post-Compaction Context Injector Documentation

## Overview

The Post-Compaction Context Injector is the second component of the Context Retention System. It automatically detects when the conversation context window has been compacted or reset, and immediately injects essential memory summaries, recent messages, and context to maintain conversational continuity.

## Features

- **Automatic Compaction Detection**: Uses multiple strategies to detect context window resets
- **Smart Memory Retrieval**: Intelligently selects the most relevant memory content
- **Prioritized Injection**: Injects the most important information first
- **Token-Aware Formatting**: Respects token limits to avoid further compactions
- **Self-Monitoring**: Can run as a background service to detect and fix compaction issues
- **Session Integration**: Seamlessly works with OpenClaw sessions
- **Testing Tools**: Includes comprehensive test suite

## Components

### 1. ContextStateManager

Tracks conversation state and detects compaction events using:
- Message hashing for duplicate detection
- Reset marker identification
- Error message pattern matching
- Session history analysis

### 2. MemoryRetriever

Retrieves relevant memory content from multiple sources:
- MEMORY.md for long-term memories
- Daily memory files
- Hourly memory summaries
- Current task context
- Recent messages

### 3. MessagingManager

Handles injecting content back into the conversation:
- Interfaces with OpenClaw messaging system
- Logs injection events
- Tracks successful injections

### 4. CompactionHandler

Coordinates the overall compaction detection and response process:
- Monitors for compaction events
- Retrieves appropriate memory
- Formats content for injection
- Triggers the injection process

### 5. Autocorrect Mechanism

Automatically detects and fixes context issues:
- Monitors for compaction indicators in real-time
- Triggers injections when needed
- Can be scheduled via cron

## Usage

### Basic Usage

```bash
# Test the injection content generation
python3 post-compaction-inject.py --test

# Simulate a compaction event
python3 post-compaction-inject.py --simulate

# Install the autocorrect mechanism
python3 post-compaction-inject.py --install-autocorrect

# Force an injection for a specific session
python3 post-compaction-inject.py --inject-now --session [SESSION_ID]

# Set up monitoring for a specific session
python3 post-compaction-inject.py --session [SESSION_ID]
```

### Setup Script

For easy setup, use the provided script:

```bash
./setup-context-injector.sh
```

This script:
1. Creates necessary directories
2. Makes scripts executable
3. Runs tests to verify functionality
4. Sets up a cron job for monitoring
5. Installs the autocorrect mechanism

## Integration Points

- **Hourly Memory Summarizer**: Pulls from summaries created by Component 1
- **MEMORY.md**: Extracts key information from long-term memory
- **Daily Memory Files**: Uses recent daily memory records
- **Task Context**: Integrates with Kanban board for current task status
- **OpenClaw Messaging**: Injects content via session messaging

## Test Suite

The system includes a comprehensive test suite:
- Unit tests for each component
- Integration tests for end-to-end functionality
- Mock tests for isolated component testing

## Future Enhancements

1. **Vector Memory Integration**: Will integrate with Component 3 (Vector Memory Pipeline)
2. **Feedback Learning**: Tracking which injected content was most useful
3. **Context-Aware Injection**: Smarter content selection based on conversation topic
4. **Multi-Session Support**: Coordinated memory across multiple sessions
5. **Performance Optimization**: Reduced token usage through better content selection

## Troubleshooting

Common issues and solutions:

1. **Injection Not Triggering**: Ensure the cron job is active and the script is executable
2. **Missing Memory Content**: Verify that memory files exist and are accessible
3. **Token Budget Exceeded**: Adjust the token limit with the --tokens parameter
4. **Session Not Found**: Make sure to provide the correct session ID

Logs can be found at `/Users/karst/.openclaw/workspace/logs/context-injector.log`