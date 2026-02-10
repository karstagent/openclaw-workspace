# Semantic Recall Hook System: User Guide

## Introduction

The Semantic Recall Hook System automatically enhances your conversations by retrieving and injecting relevant past information based on the current context. It's the final component of our Context Retention System, creating a comprehensive solution for maintaining conversational continuity.

This guide explains how to use, configure, and monitor the system.

## Quick Start

### Enable/Disable Semantic Recall

To enable semantic recall:
```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py enable
```

To disable semantic recall:
```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py disable
```

### Test the System

To test semantic recall with a specific query:
```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py test "What is the best approach for context management?"
```

This will show you what information would be injected for this query.

## Configuration

The system is configured via the `semantic-recall-config.json` file, which has these key settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `relevance_threshold` | Minimum similarity score (0.0-1.0) | 0.65 |
| `max_results` | Maximum number of results to include | 3 |
| `max_tokens` | Token budget for injected context | 1500 |
| `enabled` | Whether semantic recall is active | true |
| `token_estimation_ratio` | Characters per token (for estimation) | 4.0 |

### Changing Settings

You can change configuration values directly:

```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py config --set max_results --value 5
```

Or view current configuration:

```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py config
```

## Advanced Usage

### Monitoring and Logs

The system logs all activity to:
- `/Users/karst/.openclaw/workspace/logs/semantic-recall.log`
- `/Users/karst/.openclaw/workspace/logs/recall-history.jsonl`

The history file contains detailed records of all injections, including:
- Timestamps
- Original queries
- Results injected
- Token usage
- Source information

### Performance Tuning

For optimal performance:

1. **Finding the right threshold**:
   - Lower `relevance_threshold` (e.g., 0.55) to get more results but potentially less relevant
   - Raise it (e.g., 0.75) to get fewer but more precise results

2. **Managing token usage**:
   - Lower `max_tokens` (e.g., 800) to use less of your context window
   - Raise it (e.g., 2000) for more comprehensive context (if your model supports it)

3. **Result quantity**:
   - Lower `max_results` (e.g., 2) for focused, minimal context
   - Raise it (e.g., 5) to include more varied information

## Maintenance

### Re-indexing Vector Memory

If you've added a lot of new content to your memory files, re-index your vector memory:

```
python3 /Users/karst/.openclaw/workspace/vector-memory.py --reindex
```

### Performance Testing

Run comprehensive tests across multiple queries:

```
python3 /Users/karst/.openclaw/workspace/semantic_recall_integration_test.py --all
```

## Technical Deep Dive

### How It Works

1. **Hook Activation**: The system intercepts messages before they're processed
2. **Query Processing**: The current prompt is used to search vector memory
3. **Memory Search**: Vector embeddings find semantically similar past content
4. **Result Ranking**: Results are ranked by similarity score
5. **Token-Aware Formatting**: Content is formatted within token budget
6. **Context Injection**: Formatted content is added to the prompt
7. **Logging**: The injection is logged for future analysis

### Components

The system consists of these key modules:

1. **semantic-recall.py**: Core implementation and CLI interface
2. **semantic_recall_formatter.py**: Token-aware formatting engine
3. **vector_memory_impl.py**: Semantic search against memory
4. **semantic-recall-openclaw-commands.py**: OpenClaw command integration
5. **semantic_recall_integration_test.py**: End-to-end testing

### Integration with Context Retention System

This system completes the Context Retention System:

1. **Hourly Memory Summarizer**: Creates content that is indexed
2. **Post-Compaction Context Injector**: Restores context after compaction
3. **Vector Memory Pipeline**: Provides semantic search capabilities
4. **Semantic Recall Hook System**: Automatically enriches prompts

## Troubleshooting

### Common Issues

1. **No results being injected**:
   - Verify the system is enabled
   - Check that `relevance_threshold` isn't too high
   - Ensure your memory files are indexed

2. **Poor quality results**:
   - Reduce `relevance_threshold` to get more results
   - Re-index your memory to include latest content

3. **Too much context being added**:
   - Reduce `max_tokens` or `max_results`
   - Raise `relevance_threshold` for more precise matching

### Getting Help

For detailed diagnostics, run:

```
python3 /Users/karst/.openclaw/workspace/semantic-recall.py diagnose
```

## Conclusion

The Semantic Recall Hook System provides automatic, intelligent context enrichment for your conversations. By seamlessly integrating relevant past information, it enhances context awareness and continuity, leading to more coherent and informed interactions.

As the final component of the Context Retention System, it completes a comprehensive solution for maintaining conversational memory and context across session boundaries and context limitations.