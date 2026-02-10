# Semantic Recall Hook System Documentation

## Overview

The Semantic Recall Hook System is the fourth and final component of the Context Retention System. It implements a hook that automatically triggers semantic search against the vector memory for every prompt, injecting relevant past conversations into context before LLM processing.

## Key Features

- **Automatic Context Injection**: Seamlessly adds relevant memory to prompts
- **Semantic Search Integration**: Uses the Vector Memory Pipeline for search
- **Token-Aware Formatting**: Respects context window limits
- **Configurable Thresholds**: Adjustable relevance requirements
- **Metadata Tracking**: Complete history of injections for analysis
- **OpenClaw Integration**: Works directly with the OpenClaw hook system

## Architecture

The Semantic Recall Hook System consists of two main components:

1. **Core Hook System** (`semantic-recall.py`): The main implementation for semantic recall
2. **Installation Script** (`install-semantic-recall.py`): Setup and configuration tool

The system integrates directly with Component 3 (Vector Memory Pipeline) to search for relevant content and with OpenClaw's hook system to inject context into prompts.

## Technical Details

### Hook System

The system uses OpenClaw's pre-prompt hook mechanism to intercept prompts before they are processed. For each prompt, it:

1. Searches the vector memory for relevant content
2. Filters results based on configured thresholds
3. Formats the results for inclusion in the prompt
4. Injects the formatted text before the prompt is sent to the LLM
5. Logs the injection for future analysis

### Token Management

To respect context window limits, the system:

- Maintains a configurable token budget (`max_tokens`)
- Estimates token count using a character-to-token ratio
- Trims results to fit within the budget
- Prioritizes more relevant results when trimming

### Configuration Options

The system is highly configurable through the `semantic-recall-config.json` file:

| Option                | Default | Description                                       |
|-----------------------|---------|---------------------------------------------------|
| `relevance_threshold` | 0.65    | Minimum similarity score for inclusion            |
| `max_results`         | 3       | Maximum number of results to include              |
| `max_tokens`          | 1500    | Maximum token budget for injected context         |
| `recall_prefix`       | *       | Text to insert before injected context            |
| `recall_suffix`       | *       | Text to insert after injected context             |
| `enabled`             | true    | Whether semantic recall is active                 |
| `log_injections`      | true    | Whether to log injection events                   |
| `token_estimation_ratio` | 4.0  | Characters per token for estimation               |
| `include_sources`     | true    | Whether to include source info in injected context|
| `excluded_sessions`   | []      | Session IDs to exclude from semantic recall       |
| `context_format`      | markdown| Format for injected context (markdown or plain)   |

## Installation

The system includes an installation script that:

1. Checks dependencies (requires Vector Memory Pipeline)
2. Creates default configuration
3. Registers the hook with OpenClaw
4. Sets up OpenClaw commands
5. Indexes vector memory
6. Tests the installation

To install:

```bash
python install-semantic-recall.py
```

## Usage

### OpenClaw Commands

```
# Enable semantic recall
semantic_recall_enable

# Disable semantic recall
semantic_recall_disable

# Test semantic recall with a query
semantic_recall_test "What is the best approach for context management?"

# View or modify configuration
semantic_recall_config
```

### Direct Script Usage

```bash
# Enable semantic recall
python semantic-recall.py enable

# Disable semantic recall
python semantic-recall.py disable

# Test semantic recall with a query
python semantic-recall.py test "What is the best approach for context management?"

# View configuration
python semantic-recall.py config

# Set a configuration value
python semantic-recall.py config --set max_results --value 5

# Get a configuration value
python semantic-recall.py config --get relevance_threshold
```

## Integration with Context Retention System

The Semantic Recall Hook System completes the Context Retention System by integrating with the previous components:

1. **Hourly Memory Summarizer**: Creates content that is indexed in vector memory
2. **Post-Compaction Context Injector**: Restores context after compaction
3. **Vector Memory Pipeline**: Provides semantic search capabilities
4. **Semantic Recall Hook System**: Automatically injects relevant context for every prompt

Together, these four components form a complete system for managing context in long-running AI assistants:

- Component 1 ensures important information is captured and summarized
- Component 2 handles context recovery after compaction events
- Component 3 enables efficient semantic search of past conversations
- Component 4 proactively enriches prompts with relevant context

## Performance Considerations

- The hook adds some latency to each prompt processing
- Search operations are optimized and typically take <100ms
- Token budget is configurable to balance context richness vs. window size
- Disable for sessions that don't benefit from context enrichment

## Monitoring and Maintenance

The system logs all injections to `logs/recall-history.jsonl` for analysis. This log includes:

- Timestamps of injections
- Queries that triggered recall
- Number of results injected
- Token usage estimates
- Source information
- Similarity score ranges

This information can be used to tune the system and analyze its effectiveness.

## Future Enhancements

1. **Smarter Context Selection**: Use LLM-guided relevance assessment
2. **Query Expansion**: Enhance search with related terms
3. **Adaptive Thresholds**: Dynamically adjust based on query complexity
4. **Context Summarization**: Compress injected content for token efficiency
5. **Hybrid Search**: Combine semantic and keyword search for better results

## Troubleshooting

Common issues and solutions:

1. **No Context Injected**: Check that the system is enabled and the relevance threshold isn't too high
2. **Poor Context Quality**: Lower the relevance threshold or increase max_results
3. **Too Much Context**: Reduce max_tokens or max_results
4. **High Latency**: Ensure vector memory index is optimized
5. **Hook Not Firing**: Check hook registration and OpenClaw configuration