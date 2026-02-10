#!/usr/bin/env python3
"""
OpenAI client wrapper that transparently handles token management.
Drop-in replacement for the standard OpenAI client.
"""

import os
import sys
import importlib.util

# Add token_solutions directory to PATH
token_solutions_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "token_solutions"
)
sys.path.append(token_solutions_dir)

# Import token_solutions module
try:
    import token_solutions
    from token_solutions import TokenManagedClient
except ImportError:
    raise ImportError(
        "Token solutions not found. Please run deploy_token_solutions.sh first."
    )

# Replace standard OpenAI with managed client
from openai import OpenAI as OriginalOpenAI

class OpenAI(TokenManagedClient):
    """
    Drop-in replacement for OpenAI that transparently handles token management.
    """
    
    def __init__(self, **kwargs):
        """Initialize with an underlying OpenAI client."""
        base_client = OriginalOpenAI(**kwargs)
        super().__init__(base_client=base_client)


# Create an Anthropic wrapper as well
try:
    from anthropic import Anthropic as OriginalAnthropic
    
    class Anthropic:
        """
        Drop-in replacement for Anthropic that transparently handles token management.
        """
        
        def __init__(self, **kwargs):
            """Initialize with an Anthropic client."""
            self._base_client = OriginalAnthropic(**kwargs)
            self._api_type = "anthropic"
        
        def messages_create(self, **kwargs):
            """Override messages.create with token management."""
            return token_solutions.process_request(api_type="anthropic", **kwargs)
        
        def __getattr__(self, name):
            """Pass through other attributes to base client."""
            return getattr(self._base_client, name)
except ImportError:
    # Anthropic not installed, skip wrapper
    pass

# Create a usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAI client with token management")
    parser.add_argument("--input", "-i", required=True, help="Input file")
    parser.add_argument("--model", default="gpt-4", help="Model to use")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens to generate")
    
    args = parser.parse_args()
    
    # Create client
    client = OpenAI()
    
    # Read input
    with open(args.input, "r") as f:
        content = f.read()
    
    # Make request
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": content}],
        max_tokens=args.max_tokens
    )
    
    result = response.choices[0].message.content
    
    # Output result
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Response written to {args.output}")
    else:
        print(result)
