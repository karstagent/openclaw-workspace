#!/bin/bash
# Activate the token solutions environment
source "/Users/karst/.openclaw/workspace/token_solutions/venv/bin/activate"
export PYTHONPATH="$PYTHONPATH:/Users/karst/.openclaw/workspace/token_solutions"
export OPENAI_API_KEY="$OPENAI_API_KEY"  # Pass through if set
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"  # Pass through if set
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY"  # Pass through if set
echo "Token solutions environment activated."
echo ""
echo "Available commands:"
echo "  python /Users/karst/.openclaw/workspace/token_solutions/token_solutions.py compress --input <file> --output <file> --ratio <ratio>"
echo "  python /Users/karst/.openclaw/workspace/token_solutions/token_solutions.py extend --input <file> --model <model> --output <file>"
echo "  python /Users/karst/.openclaw/workspace/token_solutions/token_solutions.py stats"
echo ""
echo "To use as a drop-in replacement in your code:"
echo "  from token_solutions import process_request, compress_text"
echo ""
echo "Or as an OpenAI client replacement:"
echo "  import sys"
echo "  sys.path.append('/Users/karst/.openclaw/workspace/services')"
echo "  from openai_wrapper import OpenAI"
echo "  client = OpenAI()"
