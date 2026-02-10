# Semantic Recall Hook System Implementation Guide

## Overview

The Semantic Recall Hook System is the fourth and final component of the Context Retention System. This implementation guide provides detailed instructions on how to set up, configure, and integrate the system with OpenClaw.

## Prerequisites

Before implementing the Semantic Recall Hook System, ensure the following components are in place:

1. **Hourly Memory Summarizer (Component 1)** - For creating structured memory entries
2. **Post-Compaction Context Injector (Component 2)** - For handling context compaction events
3. **Vector Memory Pipeline (Component 3)** - For semantic search capabilities

The Semantic Recall system depends heavily on the Vector Memory Pipeline, so that must be fully operational before proceeding.

## Implementation Steps

### Step 1: Install Dependencies

The system requires the following Python dependencies:

- `faiss-cpu` - For vector indexing and search
- `sentence-transformers` - For creating semantic embeddings

Install these with:

```bash
pip install faiss-cpu sentence-transformers
```

### Step 2: Configure Script Files

Ensure the following files are correctly placed and configured:

1. `semantic-recall.py` - Core implementation
2. `install-semantic-recall.py` - Installation script
3. `semantic-recall-openclaw-commands.py` - OpenClaw integration
4. `semantic-recall-integration-test.py` - Integration testing

Make each script executable:

```bash
chmod +x semantic-recall.py
chmod +x install-semantic-recall.py
chmod +x semantic-recall-openclaw-commands.py
chmod +x semantic-recall-integration-test.py
```

### Step 3: Run Installation

The installation script performs several important setup tasks:

1. Verifies that all dependencies are installed
2. Creates the default configuration
3. Registers the hook with OpenClaw
4. Sets up OpenClaw commands
5. Indexes vector memory
6. Tests the installation

Run the installation script:

```bash
python install-semantic-recall.py
```

If you want to skip certain steps:

```bash
# Skip testing
python install-semantic-recall.py --skip-test

# Skip vector memory indexing
python install-semantic-recall.py --skip-index

# Force reinstallation
python install-semantic-recall.py --force
```

### Step 4: Register OpenClaw Commands

To enable easy access from OpenClaw, register the commands:

```bash
python semantic-recall-openclaw-commands.py
```

This will register the following commands:
- `/semantic_recall_enable` - Enable semantic recall
- `/semantic_recall_disable` - Disable semantic recall
- `/semantic_recall_test` - Test with a query
- `/semantic_recall_config` - View configuration
- `/semantic_recall_set` - Set configuration values
- `/semantic_recall_get` - Get specific configuration values
- `/semantic_recall_register` - Register the hook
- `/semantic_recall_unregister` - Unregister the hook

### Step 5: Run Integration Tests

Verify that all components work together correctly:

```bash
python semantic-recall-integration-test.py
```

The test script will:
1. Create test memory data
2. Index it with the Vector Memory Pipeline
3. Test semantic search functionality
4. Test context injection via the hook
5. Verify hook registration and unregistration

### Step 6: Configure the System

The default configuration can be customized by editing the `semantic-recall-config.json` file or using the configuration commands:

```bash
# View the current configuration
python semantic-recall.py config

# Set a configuration value
python semantic-recall.py config --set max_results --value 5

# Get a specific configuration value
python semantic-recall.py config --get relevance_threshold
```

Key configuration options include:

- `relevance_threshold` (default: 0.65) - Minimum similarity score for inclusion
- `max_results` (default: 3) - Maximum number of results to include
- `max_tokens` (default: 1500) - Maximum token budget for injected context
- `enabled` (default: true) - Whether semantic recall is active
- `include_sources` (default: true) - Whether to include source information
- `context_format` (default: "markdown") - Format for injected context

## Integration with OpenClaw

The Semantic Recall Hook System integrates with OpenClaw via the pre-prompt hook mechanism. When registered, the hook intercepts all prompts before they are processed by the LLM, enriches them with relevant context, and then passes them along.

### Hook Entry Point

The hook entry point is defined in `semantic-recall.py`:

```python
def hook_entry_point(prompt, session_id=None):
    """
    Entry point for OpenClaw hook system
    
    This function is called by OpenClaw before processing a prompt
    """
    config = SemanticRecallConfig()
    vector_memory = VectorMemoryPipeline()
    hook = SemanticRecallHook(config, vector_memory)
    
    injected_text, num_results, token_estimate = hook.process_prompt(prompt, session_id)
    
    if injected_text:
        logger.info(f"Injected {num_results} results ({token_estimate} tokens) for prompt")
    
    return injected_text
```

### Hook Registration

The hook is registered via a JSON file at `semantic-recall-hook.json`, which OpenClaw reads to discover and execute hooks:

```json
{
  "type": "pre_prompt",
  "name": "semantic_recall",
  "script": "/path/to/semantic-recall.py",
  "function": "hook_entry_point",
  "enabled": true,
  "registered_at": "2026-02-09T12:00:00.000Z"
}
```

## Performance Considerations

The Semantic Recall Hook System adds some processing overhead to each prompt. To minimize impact:

1. **Optimize vector search** - Keep the index size reasonable
2. **Limit max_results** - Retrieve only a few highly relevant results
3. **Set appropriate token budget** - Balance between context and token usage
4. **Use selective activation** - Disable for sessions that don't need it

## Maintenance

### Daily Indexing

For optimal performance, set up a daily indexing job to ensure the vector index stays current with new memory entries:

```bash
# Add to crontab to run daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/vector-memory.py --index
```

### Monitoring

Monitor the performance and effectiveness of the system by checking:

1. **Logs** - Check `semantic-recall.log` and `vector-memory.log`
2. **Recall History** - Review `recall-history.jsonl` to see what's being injected
3. **Configuration** - Periodically review and adjust settings

## Troubleshooting

### No Content Being Injected

If no content is being injected:

1. Verify the hook is enabled (`semantic_recall_config`)
2. Check if the relevance threshold is too high
3. Ensure vector memory is properly indexed
4. Look for errors in the logs

### Low Quality Injections

If injected content is not relevant:

1. Lower the relevance threshold
2. Increase the number of max_results
3. Improve the vector index by adding more quality memory entries

### High Token Usage

If too many tokens are being used:

1. Reduce the max_tokens setting
2. Lower the max_results setting
3. Use a more concise context format

## Complete System Overview

The Context Retention System now consists of four integrated components:

1. **Hourly Memory Summarizer** - Creates structured memory entries
2. **Post-Compaction Context Injector** - Restores context after compaction
3. **Vector Memory Pipeline** - Enables semantic search of memories
4. **Semantic Recall Hook System** - Automatically injects relevant context

Together, these components create a robust system for maintaining context in long-running AI assistants, enabling more coherent and contextually aware responses.