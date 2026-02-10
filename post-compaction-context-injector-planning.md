# Post-Compaction Context Injector Planning

## Overview

The Post-Compaction Context Injector will be the second component of our Context Retention System. This system will detect when the context window has been compacted or reset, and immediately inject essential memory summaries, recent messages, and thinking blocks to maintain continuity in conversations.

## Objectives

1. Detect context window resets or compactions
2. Inject appropriate memory content to maintain continuity
3. Prioritize the most relevant information for reinsertion
4. Operate automatically without user intervention

## System Components

### 1. Compaction Detection Module

This module will monitor for signs that the context window has been compacted:

- Message history length suddenly shortened
- Model responses indicating a lack of context awareness
- New session indicators in the conversation flow
- Explicit compaction events from the LLM platform

### 2. Memory Retrieval Module

Once compaction is detected, this module will gather essential information to be reinjected:

- Recent hourly memory summaries (last 24 hours)
- Recent direct messages from the user (last 3-5 exchanges)
- Current task and goal information
- Active project context
- Key decisions made in the conversation
- User preferences relevant to the current context

### 3. Context Injection Module

This module will format and inject the retrieved memory into the context:

- Prioritize information based on relevance to current conversation
- Format memory snippets for efficient token usage
- Use a tiered approach (essential context first, supporting details if token budget allows)
- Add metadata to track what has been reinjected

### 4. Feedback Loop

The system will learn which types of reinjected context are most useful:

- Track which reinjected information is referenced or used by the model
- Adjust future injections based on utility patterns
- Optimize token usage by focusing on high-value context

## Implementation Plan

1. Create `post-compaction-inject.py` as the main script
2. Implement compaction detection logic
3. Build memory retrieval functions
4. Develop the context injection algorithm
5. Add monitoring and logging capabilities
6. Set up automated triggering mechanisms
7. Test with various compaction scenarios

## Technical Approach

```python
# High-level pseudocode
def detect_compaction(messages):
    # Check if the context window has been compacted
    # Return True if compaction detected, False otherwise
    
def retrieve_essential_memory(current_topic=None):
    # Retrieve the most recent and relevant memory snippets
    # Prioritize based on current topic if available
    
def format_for_injection(memory_items, token_budget):
    # Format memory for injection within token budget
    # Return formatted context string
    
def inject_context(formatted_memory):
    # Inject the formatted memory into the current context
    # Log the injection event
    
def main():
    # Main monitoring loop
    while True:
        if detect_compaction(get_current_messages()):
            memory = retrieve_essential_memory()
            formatted = format_for_injection(memory, token_budget=1000)
            inject_context(formatted)
```

## Integration Points

- Integrate with hourly memory summarizer for retrieving recent summaries
- Connect with MEMORY.md for persistent context
- Interface with the messaging system for injection
- Prepare groundwork for vector memory integration (Phase 3)

## Success Criteria

1. System successfully detects >95% of compaction events
2. Essential context is restored within 1 message exchange
3. Injected context is relevant to the current conversation
4. Users report minimal discontinuity in conversation flow
5. Token usage stays within efficient parameters

## Next Steps

1. Design detailed data structures for memory retrieval
2. Implement compaction detection algorithms
3. Create the core injection mechanisms
4. Develop monitoring and feedback systems
5. Set up integration tests with the hourly memory summarizer