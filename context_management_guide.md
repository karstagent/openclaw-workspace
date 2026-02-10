# OpenClaw Context Management System

This system prevents OpenClaw from encountering the "LLM request rejected: input length and max_tokens exceed context limit" error by intelligently managing the context window size.

## Overview

The Context Management System:

1. Monitors outgoing LLM API requests
2. Detects when total tokens would exceed context limits
3. Intelligently trims conversation history while preserving important messages
4. Adjusts max_tokens if necessary to ensure requests succeed
5. Logs all actions for transparency

## Installation

1. Ensure the following Python files are installed in your OpenClaw workspace:
   - `context_manager.py` - Core token management logic
   - `context_middleware.py` - Middleware implementation
   - `openclaw_context_handler.py` - OpenClaw integration

2. Make the handler script executable:
   ```bash
   chmod +x /Users/karst/.openclaw/workspace/openclaw_context_handler.py
   ```

3. Create a logs directory for the system:
   ```bash
   mkdir -p /Users/karst/.openclaw/workspace/logs
   ```

## Integration Options

### Option 1: OpenClaw Plugin/Hook (Recommended)

If OpenClaw supports pre-processing hooks for LLM requests, configure it to use the context handler:

1. Edit your OpenClaw configuration to include:
   ```json
   {
     "llm": {
       "preprocessors": [
         {
           "type": "script",
           "path": "/Users/karst/.openclaw/workspace/openclaw_context_handler.py"
         }
       ]
     }
   }
   ```

### Option 2: API Proxy

Set up the context handler as a local API proxy between OpenClaw and the LLM provider:

1. Create a proxy service using the context handler
2. Configure OpenClaw to use your local proxy URL instead of the direct API URL

### Option 3: Manual Integration

For testing or in cases where hooks are not available:

1. Call the context handler manually before sending requests
2. Process the response and forward to the LLM API

## Configuration

Create a configuration file at `/Users/karst/.openclaw/workspace/context_config.json` to customize behavior:

```json
{
  "max_context": 200000,
  "buffer": 10000,
  "log_level": "INFO",
  "strategies": {
    "prefer_recent_messages": true,
    "preserve_system_messages": true,
    "summarize_removed_messages": true
  }
}
```

## Monitoring and Troubleshooting

Logs are stored in `/Users/karst/.openclaw/workspace/logs/`:

- `context_manager.log` - Core token management logs
- `context_middleware.log` - Middleware processing logs
- `openclaw_context_handler.log` - OpenClaw integration logs

## Testing

Run the included test script to verify your installation:

```bash
python3 /Users/karst/.openclaw/workspace/test_context_manager.py
```

## How It Works

1. **Token Counting**: The system estimates token counts for all messages.
   
2. **Message Prioritization**: Messages are categorized by importance:
   - System messages (highest priority)
   - Recent messages (high priority)
   - Older messages (lower priority)
   
3. **Intelligent Trimming**: If token limits would be exceeded, the system:
   - Removes older messages first
   - Preserves system messages
   - Keeps recent conversation intact
   - Optionally adds a summary of removed content
   
4. **Max Tokens Adjustment**: If needed, max_tokens is reduced to fit within limits.

5. **Request Transformation**: The modified request is sent to the LLM API.

## Advanced Usage

### Custom Trimming Strategies

You can customize the trimming strategy by modifying the `trim_messages` method in `context_manager.py`.

### Context-Aware Processing

For specialized applications, you can extend the system to be aware of specific message patterns or content types that should be preserved.

### Integration with Memory Systems

This system can be combined with long-term memory solutions to ensure that critical information is never lost, even when messages are trimmed.

## Troubleshooting

If you encounter issues:

1. Check the logs for detailed information
2. Verify your configuration file is correctly formatted
3. Test with the included test script
4. Try adjusting max_context and buffer values

For persistent problems, contact OpenClaw support with your log files.