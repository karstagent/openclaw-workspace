#!/usr/bin/env python3
"""
Installation script for the Semantic Recall Hook System

This script installs and configures the Semantic Recall Hook System,
the fourth component of the Context Retention System.
"""

import os
import sys
import json
import logging
import subprocess
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("semantic-recall-install.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('install')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
SCRIPT_PATH = os.path.join(WORKSPACE_DIR, "semantic-recall.py")
VECTOR_MEMORY_PATH = os.path.join(WORKSPACE_DIR, "vector-memory.py")
CONFIG_PATH = os.path.join(WORKSPACE_DIR, "semantic-recall-config.json")
HOOK_PATH = os.path.join(WORKSPACE_DIR, "semantic-recall-hook.json")
OPENCLAW_SCRIPT = "openclaw"

def check_dependencies():
    """Check if all required dependencies are installed"""
    # Check if vector memory is implemented
    if not os.path.exists(VECTOR_MEMORY_PATH):
        logger.error("Vector Memory Pipeline not found")
        logger.error("Please implement the Vector Memory Pipeline (component 3) first")
        return False
    
    # Check if Python dependencies are installed
    try:
        import vector_memory
        logger.info("Vector Memory module found")
    except ImportError:
        logger.error("Vector Memory module not found")
        logger.error("Please implement the Vector Memory Pipeline (component 3) first")
        return False
    
    return True

def make_executable(script_path):
    """Make the script executable"""
    try:
        os.chmod(script_path, 0o755)
        logger.info(f"Made executable: {script_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to make executable: {e}")
        return False

def create_default_config():
    """Create default configuration file"""
    config = {
        "relevance_threshold": 0.65,
        "max_results": 3,
        "max_tokens": 1500,
        "recall_prefix": "# Recent Relevant Context\n\n",
        "recall_suffix": "\n\nConsider the above context in your response.\n\n",
        "enabled": True,
        "log_injections": True,
        "token_estimation_ratio": 4.0,
        "include_sources": True,
        "excluded_sessions": [],
        "context_format": "markdown",
        "last_updated": datetime.now().isoformat()
    }
    
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Created default config at {CONFIG_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to create default config: {e}")
        return False

def register_hook():
    """Register the hook with OpenClaw"""
    try:
        # Use the script's register command
        cmd = [sys.executable, SCRIPT_PATH, "register"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Registered semantic recall hook")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to register hook: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Error: {e.stderr}")
        return False

def setup_openclaw_commands():
    """
    Register the semantic recall commands with OpenClaw
    """
    script_path = os.path.abspath(SCRIPT_PATH)
    
    # Define the commands to register
    commands = [
        {
            "name": "semantic_recall_enable",
            "script": script_path,
            "args": ["enable"],
            "description": "Enable semantic recall for automatic context injection"
        },
        {
            "name": "semantic_recall_disable",
            "script": script_path,
            "args": ["disable"],
            "description": "Disable semantic recall"
        },
        {
            "name": "semantic_recall_test",
            "script": script_path,
            "args": ["test", "${query}"],
            "description": "Test semantic recall with a query"
        },
        {
            "name": "semantic_recall_config",
            "script": script_path,
            "args": ["config"],
            "description": "View or modify semantic recall configuration"
        }
    ]
    
    # Register each command with OpenClaw
    success = True
    for cmd in commands:
        try:
            # Prepare the command definition
            cmd_json = json.dumps(cmd)
            
            # Run openclaw command to register
            openclaw_cmd = [
                OPENCLAW_SCRIPT,
                "command",
                "register",
                cmd_json
            ]
            
            subprocess.run(openclaw_cmd, capture_output=True, text=True, check=True)
            logger.info(f"Registered OpenClaw command: {cmd['name']}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to register command {cmd['name']}: {e}")
            logger.error(f"Error output: {e.stderr}")
            success = False
    
    return success

def test_recall():
    """Test the semantic recall system"""
    try:
        # Use the script's test command with a sample prompt
        cmd = [sys.executable, SCRIPT_PATH, "test", "What is the best way to implement semantic search for context?"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\nTest results:")
        print(process.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Test failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def index_vector_memory():
    """Index vector memory to ensure it's ready for semantic recall"""
    try:
        # Use the vector memory script to run indexing
        cmd = [sys.executable, VECTOR_MEMORY_PATH, "--index"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Indexed vector memory")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to index vector memory: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install Semantic Recall Hook System")
    parser.add_argument("--force", action="store_true", help="Force reinstallation")
    parser.add_argument("--skip-test", action="store_true", help="Skip testing")
    parser.add_argument("--skip-index", action="store_true", help="Skip vector memory indexing")
    args = parser.parse_args()
    
    print("Semantic Recall Hook System Installation\n")
    
    # Check if already installed
    if os.path.exists(CONFIG_PATH) and os.path.exists(HOOK_PATH) and not args.force:
        print("Semantic Recall Hook System appears to be already installed.")
        print("Use --force to reinstall.")
        
        confirm = input("Would you like to continue anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("Installation cancelled.")
            sys.exit(0)
    
    # Step 1: Check dependencies
    print("\n[1/7] Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please fix the issues and try again.")
        print("Installation aborted.")
        sys.exit(1)
    
    # Step 2: Make script executable
    print("\n[2/7] Making script executable...")
    if not make_executable(SCRIPT_PATH):
        print("\n⚠️ Failed to make script executable.")
        print("Installation will continue, but you may need to manually set permissions.")
    
    # Step 3: Create default configuration
    print("\n[3/7] Creating default configuration...")
    if not create_default_config():
        print("\n❌ Failed to create default configuration.")
        print("Installation aborted.")
        sys.exit(1)
    
    # Step 4: Register the hook
    print("\n[4/7] Registering the hook with OpenClaw...")
    if not register_hook():
        print("\n⚠️ Failed to register the hook with OpenClaw.")
        print("Installation will continue, but hook integration may not work.")
    
    # Step 5: Set up OpenClaw commands
    print("\n[5/7] Setting up OpenClaw commands...")
    if not setup_openclaw_commands():
        print("\n⚠️ Failed to set up some OpenClaw commands.")
        print("Installation will continue, but some commands may not work.")
    
    # Step 6: Index vector memory
    if not args.skip_index:
        print("\n[6/7] Indexing vector memory...")
        if not index_vector_memory():
            print("\n⚠️ Failed to index vector memory.")
            print("Installation will continue, but semantic recall may not work properly.")
    else:
        print("\n[6/7] Skipping vector memory indexing (--skip-index)")
    
    # Step 7: Test the installation
    if not args.skip_test:
        print("\n[7/7] Testing the installation...")
        if not test_recall():
            print("\n⚠️ Test failed.")
            print("Installation will continue, but semantic recall may not work properly.")
    else:
        print("\n[7/7] Skipping test (--skip-test)")
    
    # Completion
    print("\n✅ Semantic Recall Hook System installed successfully!")
    print("\nAvailable OpenClaw commands:")
    print("  semantic_recall_enable  - Enable semantic recall")
    print("  semantic_recall_disable - Disable semantic recall")
    print("  semantic_recall_test    - Test semantic recall with a query")
    print("  semantic_recall_config  - View or modify configuration")
    
    print("\nYou can also use the script directly:")
    print(f"  python {SCRIPT_PATH} enable")
    print(f"  python {SCRIPT_PATH} disable")
    print(f"  python {SCRIPT_PATH} test \"your query here\"")
    print(f"  python {SCRIPT_PATH} config")
    
    print("\nInstallation completed at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
if __name__ == "__main__":
    main()