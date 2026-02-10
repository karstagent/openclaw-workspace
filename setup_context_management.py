#!/usr/bin/env python3
"""
OpenClaw Context Management Integration Script

This script sets up the context management system for OpenClaw
and configures it to intercept and process LLM API requests.

Usage:
  python3 setup_context_management.py [--install|--uninstall|--status]

Options:
  --install    Install and enable the context management system
  --uninstall  Remove the context management system
  --status     Check if the context management system is installed
  --test       Run a test to verify the system works correctly
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path

# Define paths
WORKSPACE_DIR = Path('/Users/karst/.openclaw/workspace')
SCRIPTS_DIR = WORKSPACE_DIR
LOGS_DIR = WORKSPACE_DIR / "logs"
CONFIG_PATH = WORKSPACE_DIR / "context_config.json"
OPENCLAW_CONFIG_DIR = Path('/Users/karst/.openclaw/config')
OPENCLAW_CONFIG_PATH = OPENCLAW_CONFIG_DIR / "config.json"

# Required files
REQUIRED_FILES = [
    SCRIPTS_DIR / "context_manager.py",
    SCRIPTS_DIR / "context_middleware.py", 
    SCRIPTS_DIR / "openclaw_context_handler.py"
]

def check_installation():
    """
    Check if the context management system is installed.
    
    Returns:
        Tuple of (files_installed, configured_in_openclaw)
    """
    # Check if all required files exist
    files_installed = all(f.exists() for f in REQUIRED_FILES)
    
    # Check if configured in OpenClaw config
    configured_in_openclaw = False
    if OPENCLAW_CONFIG_PATH.exists():
        try:
            with open(OPENCLAW_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                
            # Check if our handler is in preprocessors
            if 'llm' in config and 'preprocessors' in config['llm']:
                for preprocessor in config['llm'].get('preprocessors', []):
                    if preprocessor.get('type') == 'script' and \
                       preprocessor.get('path') == str(SCRIPTS_DIR / "openclaw_context_handler.py"):
                        configured_in_openclaw = True
                        break
        except Exception as e:
            print(f"Error checking OpenClaw configuration: {str(e)}")
    
    return files_installed, configured_in_openclaw

def create_default_config():
    """Create default configuration file if it doesn't exist"""
    if not CONFIG_PATH.exists():
        default_config = {
            "max_context": 200000,
            "buffer": 10000,
            "log_level": "INFO",
            "strategies": {
                "prefer_recent_messages": True,
                "preserve_system_messages": True,
                "summarize_removed_messages": True
            }
        }
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default configuration at {CONFIG_PATH}")

def install():
    """Install the context management system"""
    # Check if already installed
    files_installed, configured_in_openclaw = check_installation()
    
    if files_installed and configured_in_openclaw:
        print("Context management system is already installed and configured.")
        return
    
    # Create logs directory
    LOGS_DIR.mkdir(exist_ok=True)
    print(f"Created logs directory at {LOGS_DIR}")
    
    # Make scripts executable
    for script in REQUIRED_FILES:
        if script.exists() and script.suffix == '.py':
            os.chmod(script, 0o755)
            print(f"Made {script} executable")
    
    # Create default configuration
    create_default_config()
    
    # Configure OpenClaw if possible
    if not configured_in_openclaw and OPENCLAW_CONFIG_PATH.exists():
        try:
            # Read current config
            with open(OPENCLAW_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            # Add our preprocessor
            if 'llm' not in config:
                config['llm'] = {}
            
            if 'preprocessors' not in config['llm']:
                config['llm']['preprocessors'] = []
            
            # Add our handler if not already present
            handler_path = str(SCRIPTS_DIR / "openclaw_context_handler.py")
            for preprocessor in config['llm'].get('preprocessors', []):
                if preprocessor.get('type') == 'script' and preprocessor.get('path') == handler_path:
                    break
            else:
                # Not found, add it
                config['llm']['preprocessors'].append({
                    "type": "script",
                    "path": handler_path
                })
            
            # Write updated config
            with open(OPENCLAW_CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Updated OpenClaw configuration at {OPENCLAW_CONFIG_PATH}")
            print("You'll need to restart OpenClaw for the changes to take effect")
        except Exception as e:
            print(f"Error updating OpenClaw configuration: {str(e)}")
            print("You'll need to manually configure OpenClaw to use the context handler")
    
    print("\nContext management system has been installed.")
    print(f"The logs will be available at {LOGS_DIR}")
    print(f"You can modify configuration at {CONFIG_PATH}")

def uninstall():
    """Uninstall the context management system"""
    # Check if installed
    files_installed, configured_in_openclaw = check_installation()
    
    if not files_installed and not configured_in_openclaw:
        print("Context management system is not installed.")
        return
    
    # Remove from OpenClaw config
    if configured_in_openclaw and OPENCLAW_CONFIG_PATH.exists():
        try:
            # Read current config
            with open(OPENCLAW_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            # Remove our preprocessor
            if 'llm' in config and 'preprocessors' in config['llm']:
                handler_path = str(SCRIPTS_DIR / "openclaw_context_handler.py")
                config['llm']['preprocessors'] = [
                    p for p in config['llm']['preprocessors'] 
                    if not (p.get('type') == 'script' and p.get('path') == handler_path)
                ]
            
            # Write updated config
            with open(OPENCLAW_CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Removed from OpenClaw configuration at {OPENCLAW_CONFIG_PATH}")
            print("You'll need to restart OpenClaw for the changes to take effect")
        except Exception as e:
            print(f"Error updating OpenClaw configuration: {str(e)}")
    
    print("\nContext management system has been uninstalled from OpenClaw configuration.")
    print("The script files remain in your workspace. To completely remove, delete:")
    for f in REQUIRED_FILES:
        print(f"- {f}")

def status():
    """Show status of the context management system"""
    files_installed, configured_in_openclaw = check_installation()
    
    print("OpenClaw Context Management System Status:")
    print(f"- Required files: {'✅ Installed' if files_installed else '❌ Not installed'}")
    print(f"- OpenClaw configuration: {'✅ Configured' if configured_in_openclaw else '❌ Not configured'}")
    
    if CONFIG_PATH.exists():
        print(f"- Configuration: ✅ {CONFIG_PATH}")
    else:
        print(f"- Configuration: ❌ {CONFIG_PATH} not found")
    
    if LOGS_DIR.exists():
        log_files = list(LOGS_DIR.glob("*context*.log"))
        if log_files:
            print(f"- Logs: ✅ {len(log_files)} log files found in {LOGS_DIR}")
        else:
            print(f"- Logs: ℹ️ Log directory exists but no logs found yet")
    else:
        print(f"- Logs: ❌ {LOGS_DIR} not found")
    
    # Show OpenClaw restart required if needed
    if files_installed and configured_in_openclaw:
        print("\nThe system is fully installed and configured.")
    elif files_installed and not configured_in_openclaw:
        print("\nThe files are installed but OpenClaw is not configured to use them.")
        print("Run this script with --install to configure OpenClaw.")
    elif not files_installed:
        print("\nThe system is not fully installed.")
        print("Run this script with --install to install.")

def test():
    """Run a test to verify the system works correctly"""
    test_script = SCRIPTS_DIR / "test_context_manager.py"
    if not test_script.exists():
        print(f"❌ Test script not found at {test_script}")
        return
    
    print("Running context management system test...")
    os.system(f"python3 {test_script}")

def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(description="OpenClaw Context Management Integration")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--install', action='store_true', help='Install and enable the system')
    group.add_argument('--uninstall', action='store_true', help='Remove the system')
    group.add_argument('--status', action='store_true', help='Check if the system is installed')
    group.add_argument('--test', action='store_true', help='Run a test to verify the system works correctly')
    
    args = parser.parse_args()
    
    if args.install:
        install()
    elif args.uninstall:
        uninstall()
    elif args.test:
        test()
    else:
        # Default to status
        status()

if __name__ == "__main__":
    main()