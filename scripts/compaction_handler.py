#!/usr/bin/env python3
import sys
import os
import re
import logging
import json
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/compaction-handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('compaction-handler')

def handle_message(message):
    """Check if message indicates context compaction and run injector if needed"""
    compaction_indicators = [
        "input length .* exceed context limit",
        "context (?:window|limit) .* exceed",
        "token limit exceed",
        "context .* full",
        "I don't have access to that information",
        "I don't have that context",
        "I don't have memory of that"
    ]
    
    # Extract session info
    session_match = re.search(r"session[_\s]*(?:id|key)[:\s]*([\w-]+)", message, re.IGNORECASE)
    session_id = session_match.group(1) if session_match else None
    
    if not session_id:
        # Try to get from environment
        session_id = os.environ.get("OPENCLAW_SESSION_ID")
    
    if not session_id:
        logger.error("Could not determine session ID")
        return
    
    # Check for compaction indicators
    for pattern in compaction_indicators:
        if re.search(pattern, message, re.IGNORECASE):
            logger.info(f"Compaction indicator detected: {pattern}")
            
            # Run the injector
            try:
                subprocess.run(
                    ["/Users/karst/.openclaw/workspace/post-compaction-inject.py", "--session", session_id, "--inject-now"],
                    check=True
                )
                logger.info(f"Ran context injector for session {session_id}")
                return
            except Exception as e:
                logger.error(f"Failed to run context injector: {e}")
                return
    
    logger.debug("No compaction indicators detected")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
        handle_message(message)
    else:
        # Read from stdin
        message = sys.stdin.read()
        handle_message(message)
