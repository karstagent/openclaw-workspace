# Context Management System for OpenClaw

## Problem Solved

This system prevents the "LLM request rejected: input length and max_tokens exceed context limit" error by intelligently managing the context window size before requests are sent to the API.

## Implementation Components

1. **Core Context Manager** (`context_manager.py`)
   - Estimates token usage for messages
   - Implements intelligent trimming strategies
   - Preserves important messages (system prompts, recent conversation)
   - Adjusts max_tokens when needed

2. **Middleware Layer** (`context_middleware.py`)
   - Integrates with API clients
   - Handles preprocessing of requests
   - Provides logging and error handling

3. **OpenClaw Handler** (`openclaw_context_handler.py`)
   - Specifically designed for OpenClaw integration
   - Handles JSON request format conversions
   - Provides command-line interface for standalone use

4. **Test Script** (`test_context_manager.py`)
   - Generates test cases that would exceed context limits
   - Demonstrates how the system manages them
   - Provides metrics on token reduction

5. **Setup Script** (`setup_context_management.py`)
   - Installs and configures the system
   - Updates OpenClaw configuration (when possible)
   - Provides status reporting

6. **Documentation** (`context_management_guide.md`)
   - Explains the system architecture
   - Provides integration instructions
   - Includes troubleshooting guidance

## How It Works

1. **Before**: OpenClaw sends a request to the LLM API
   - If total tokens (input + max_tokens) exceeds the limit, the API rejects it
   - User sees an error message

2. **After**: OpenClaw sends a request through our context manager
   - System checks if total tokens would exceed limits
   - If so, it intelligently trims conversation history
   - It prioritizes important messages (system, recent)
   - It adjusts max_tokens if necessary
   - Modified request is sent to the API and succeeds
   - User never sees an error

## Key Features

- **Intelligent Trimming**: Removes less important messages first
- **Preservation Logic**: Keeps system messages and recent conversation intact
- **Transparent Operation**: Logs all actions for visibility
- **Configurable Behavior**: Custom limits, buffer sizes, and strategies
- **Easy Integration**: Works with OpenClaw's configuration system
- **Minimal Impact**: Only modifies requests when necessary

## Benefits

1. **Improved Reliability**: Eliminates context limit errors
2. **Better User Experience**: No more failed requests
3. **Optimized Token Usage**: Smartly trims to exactly what's needed
4. **Transparent Operation**: Detailed logs for troubleshooting
5. **Minimal Disruption**: Works behind the scenes

## Usage

To use the system:

1. Run `python3 /Users/karst/.openclaw/workspace/setup_context_management.py --install`
2. Restart OpenClaw for changes to take effect
3. Monitor logs in `/Users/karst/.openclaw/workspace/logs/` to see it in action

## Testing

Test the system with:
```bash
python3 /Users/karst/.openclaw/workspace/test_context_manager.py
```

## Next Steps

- Monitor the system in production
- Fine-tune the configuration based on usage patterns
- Consider implementing more advanced trimming strategies
- Add support for specialized content preservation (code blocks, etc.)