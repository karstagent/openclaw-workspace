#!/usr/bin/env python3
"""
OpenClaw Context Management Integration

This script integrates the context management system with OpenClaw to prevent
context window limit errors. It acts as a proxy/middleware that intercepts
LLM requests, optimizes them to fit within context limits, and then forwards
them to the actual LLM API.

Usage:
1. Configure the script with your OpenClaw settings
2. Set up as a pre-processor for LLM requests in your OpenClaw config
3. Monitor logs to see context optimizations
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to sys.path if running as standalone script
sys.path.insert(0, str(Path(__file__).parent))

# Import our context management modules
from context_manager import ContextManager
from context_middleware import ContextMiddleware

# Set up logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "openclaw_context_manager.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("openclaw_context")

class OpenClawContextHandler:
    """
    Context management handler specifically designed for OpenClaw integration.
    """
    
    def __init__(self, config=None):
        """
        Initialize the handler with optional configuration.
        
        Args:
            config: Configuration dictionary with custom settings
        """
        self.config = config or {}
        
        # Initialize context manager with custom settings if provided
        max_context = self.config.get("max_context", 200000)
        buffer = self.config.get("buffer", 10000)
        self.context_manager = ContextManager(max_context=max_context, buffer=buffer)
        
        # Initialize middleware
        self.middleware = ContextMiddleware(context_manager=self.context_manager)
        
        logger.info(f"Initialized OpenClaw Context Handler (max_context={max_context}, buffer={buffer})")
    
    def process_request(self, request_data):
        """
        Process an OpenClaw LLM request.
        
        Args:
            request_data: Dictionary or JSON string containing the LLM request
            
        Returns:
            Processed request data that will fit within context limits
        """
        # Convert JSON string to dict if needed
        if isinstance(request_data, str):
            try:
                request_data = json.loads(request_data)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON request")
                return request_data
        
        # Log request details
        model = request_data.get("model", "unknown")
        msg_count = len(request_data.get("messages", []))
        max_tokens = request_data.get("max_tokens", "default")
        
        logger.info(f"Processing request: model={model}, messages={msg_count}, max_tokens={max_tokens}")
        
        # Apply middleware processing
        try:
            processed_data = self.middleware.process_request(request_data)
            
            # Log changes
            new_msg_count = len(processed_data.get("messages", []))
            new_max_tokens = processed_data.get("max_tokens", "default")
            
            if msg_count != new_msg_count or max_tokens != new_max_tokens:
                logger.info(f"Modified request: messages {msg_count}->{new_msg_count}, " +
                           f"max_tokens {max_tokens}->{new_max_tokens}")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return request_data

def main():
    """Command-line entry point for standalone usage"""
    parser = argparse.ArgumentParser(description="OpenClaw Context Management")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--input", type=str, help="Input request file or JSON string")
    parser.add_argument("--output", type=str, help="Output file path (stdout if not specified)")
    args = parser.parse_args()
    
    # Load config if specified
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize handler
    handler = OpenClawContextHandler(config)
    
    # Get input
    request_data = None
    if args.input:
        # Check if input is a file
        if os.path.exists(args.input):
            with open(args.input, 'r') as f:
                request_data = json.load(f)
        else:
            # Treat as JSON string
            try:
                request_data = json.loads(args.input)
            except json.JSONDecodeError:
                logger.error("Failed to parse input as JSON")
                sys.exit(1)
    else:
        # Read from stdin
        try:
            request_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            logger.error("Failed to parse stdin as JSON")
            sys.exit(1)
    
    # Process request
    processed_data = handler.process_request(request_data)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(processed_data, f, indent=2)
    else:
        json.dump(processed_data, sys.stdout, indent=2)

if __name__ == "__main__":
    main()