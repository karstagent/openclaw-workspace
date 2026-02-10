#!/usr/bin/env python3
"""
OpenClaw Command Integration for Semantic Recall Hook System

This script provides OpenClaw command integration for the Semantic Recall
Hook System, allowing users to control and test the system directly through
OpenClaw commands.
"""

import os
import sys
import json
import subprocess
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/semantic-recall-commands.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('semantic-recall-commands')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
CONFIG_FILE = os.path.join(WORKSPACE_DIR, "semantic-recall-config.json")
SEMANTIC_RECALL_SCRIPT = os.path.join(WORKSPACE_DIR, "semantic-recall.py")

def get_openclaw_script():
    """Get the openclaw script path"""
    return "openclaw"

def register_commands():
    """Register semantic recall commands with OpenClaw"""
    openclaw = get_openclaw_script()
    
    commands = [
        {
            "name": "semantic_recall_enable",
            "description": "Enable semantic recall for automatic context injection",
            "action": f"python3 {SEMANTIC_RECALL_SCRIPT} enable"
        },
        {
            "name": "semantic_recall_disable",
            "description": "Disable semantic recall",
            "action": f"python3 {SEMANTIC_RECALL_SCRIPT} disable"
        },
        {
            "name": "semantic_recall_status",
            "description": "Show semantic recall status and configuration",
            "action": f"python3 {SEMANTIC_RECALL_SCRIPT} status"
        },
        {
            "name": "semantic_recall_test",
            "description": "Test semantic recall with a query",
            "action": f"python3 {SEMANTIC_RECALL_SCRIPT} test \"$1\""
        },
        {
            "name": "semantic_recall_config",
            "description": "View or modify semantic recall configuration",
            "action": f"python3 {SEMANTIC_RECALL_SCRIPT} config"
        }
    ]
    
    # Create command registration file
    commands_file = os.path.join(WORKSPACE_DIR, "semantic-recall-commands.json")
    with open(commands_file, 'w') as f:
        json.dump(commands, f, indent=2)
    
    # Register commands
    for cmd in commands:
        try:
            result = subprocess.run(
                [openclaw, "command", "register", cmd["name"], 
                 "--description", cmd["description"], 
                 "--run", cmd["action"]],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to register command {cmd['name']}: {result.stderr}")
            else:
                logger.info(f"Registered command: {cmd['name']}")
                
        except Exception as e:
            logger.error(f"Error registering command {cmd['name']}: {str(e)}")
    
    return True

def test_commands():
    """Test that commands are registered properly"""
    openclaw = get_openclaw_script()
    
    try:
        result = subprocess.run(
            [openclaw, "command", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to list commands: {result.stderr}")
            return False
            
        output = result.stdout
        
        # Check if our commands are registered
        command_names = [
            "semantic_recall_enable", 
            "semantic_recall_disable",
            "semantic_recall_test",
            "semantic_recall_config"
        ]
        
        missing_commands = []
        for cmd in command_names:
            if cmd not in output:
                missing_commands.append(cmd)
                
        if missing_commands:
            logger.warning(f"Some commands are not registered: {missing_commands}")
            return False
            
        logger.info("All commands are properly registered")
        return True
        
    except Exception as e:
        logger.error(f"Error testing commands: {str(e)}")
        return False

def create_sample_config():
    """Create a sample configuration if none exists"""
    if not os.path.exists(CONFIG_FILE):
        config = {
            "enabled": True,
            "relevance_threshold": 0.65,
            "max_results": 3,
            "max_tokens": 1500,
            "token_estimation_ratio": 4.0,
            "include_sources": True,
            "context_format": "markdown",
            "recall_prefix": "# Relevant Context\n\n*Semantic recall detected relevant information*\n\n",
            "recall_suffix": "\n\n---\n\n",
            "excluded_sessions": []
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Created sample configuration at {CONFIG_FILE}")
        return True
    
    return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Semantic Recall OpenClaw Command Integration")
    parser.add_argument("--register", action="store_true", help="Register commands with OpenClaw")
    parser.add_argument("--test", action="store_true", help="Test command registration")
    args = parser.parse_args()
    
    # Create sample config if needed
    create_sample_config()
    
    if args.register:
        register_commands()
        
    if args.test:
        success = test_commands()
        return 0 if success else 1
        
    # Default behavior: register commands
    if not args.register and not args.test:
        register_commands()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())