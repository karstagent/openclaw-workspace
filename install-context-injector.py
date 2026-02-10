#!/usr/bin/env python3
"""
Installation script for the Post-Compaction Context Injector.

This script sets up the necessary cron jobs and directories for
automatic monitoring and correction of context compaction events.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("context-injector-install.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('install')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
SCRIPT_PATH = os.path.join(WORKSPACE_DIR, "post-compaction-inject.py")
OPENCLAW_SCRIPT = "openclaw"

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        os.path.join(WORKSPACE_DIR, "logs"),
        os.path.join(WORKSPACE_DIR, "memory"),
        os.path.join(WORKSPACE_DIR, "memory", "hourly-summaries"),
        os.path.join(WORKSPACE_DIR, "scripts"),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def make_executable(script_path):
    """Make the script executable"""
    try:
        os.chmod(script_path, 0o755)
        logger.info(f"Made executable: {script_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to make executable: {e}")
        return False

def setup_cron_job(job_name, schedule, payload, session_target="main"):
    """Set up a cron job"""
    try:
        job_data = {
            "name": job_name,
            "schedule": schedule,
            "payload": payload,
            "sessionTarget": session_target,
            "enabled": True
        }
        
        cmd = [
            OPENCLAW_SCRIPT,
            "cron",
            "action=add",
            f"job={json.dumps(job_data)}"
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info(f"Successfully set up cron job: {job_name}")
            return True
        else:
            logger.error(f"Failed to set up cron job: {process.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error setting up cron job: {e}")
        return False

def test_script():
    """Test the script to ensure it works"""
    try:
        process = subprocess.run(
            ["python3", SCRIPT_PATH, "--test"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info("Script test passed")
            print("\nScript test output:")
            print(process.stdout)
            return True
        else:
            logger.error(f"Script test failed: {process.stderr}")
            print("\nScript test error:")
            print(process.stderr)
            return False
    except Exception as e:
        logger.error(f"Error testing script: {e}")
        return False

def install_scheduled_checks():
    """Set up scheduled checks for context compaction"""
    # Define our cron jobs
    cron_jobs = [
        {
            "name": "context-compaction-monitor-10m",
            "schedule": {
                "kind": "every",
                "everyMs": 600000  # Every 10 minutes
            },
            "payload": {
                "kind": "systemEvent",
                "text": "Running context compaction monitor (10-minute check)"
            }
        },
        {
            "name": "context-compaction-autocorrect",
            "schedule": {
                "kind": "every",
                "everyMs": 300000  # Every 5 minutes
            },
            "payload": {
                "kind": "agentTurn",
                "message": "Check for any messages indicating context compaction issues and run the context injector if needed."
            },
            "session_target": "isolated"
        }
    ]
    
    success = True
    for job in cron_jobs:
        job_success = setup_cron_job(
            job["name"],
            job["schedule"],
            job["payload"],
            job.get("session_target", "main")
        )
        success = success and job_success
    
    return success

def install_autocorrect():
    """Install the autocorrect mechanism"""
    try:
        process = subprocess.run(
            ["python3", SCRIPT_PATH, "--install-autocorrect"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info("Autocorrect mechanism installed")
            return True
        else:
            logger.error(f"Failed to install autocorrect: {process.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing autocorrect: {e}")
        return False

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install Context Injector")
    parser.add_argument("--force", action="store_true", help="Force reinstallation")
    parser.add_argument("--check-only", action="store_true", help="Only check if installation is needed")
    args = parser.parse_args()
    
    print("Post-Compaction Context Injector Installation\n")
    
    # Step 1: Check if already installed
    if os.path.exists(os.path.join(WORKSPACE_DIR, "context-state.json")) and not args.force:
        print("Context Injector appears to be already installed.")
        print("Use --force to reinstall anyway.")
        
        if args.check_only:
            sys.exit(0)
        
        confirm = input("Would you like to continue anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("Installation cancelled.")
            sys.exit(0)
    
    if args.check_only:
        print("Installation check completed. Installation needed.")
        sys.exit(0)
    
    # Step 2: Ensure directories
    print("\n[1/6] Ensuring directories exist...")
    ensure_directories()
    
    # Step 3: Make script executable
    print("\n[2/6] Making script executable...")
    make_executable(SCRIPT_PATH)
    
    # Step 4: Test the script
    print("\n[3/6] Testing script functionality...")
    if not test_script():
        print("\n❌ Script test failed. Please check the log for details.")
        print("Installation aborted.")
        sys.exit(1)
    
    # Step 5: Set up scheduled checks
    print("\n[4/6] Setting up scheduled checks...")
    if not install_scheduled_checks():
        print("\n⚠️ Failed to set up some scheduled checks.")
        print("Installation will continue, but some features may not work.")
    
    # Step 6: Install autocorrect
    print("\n[5/6] Installing autocorrect mechanism...")
    if not install_autocorrect():
        print("\n⚠️ Failed to install autocorrect mechanism.")
        print("Installation will continue, but automatic correction may not work.")
    
    # Step 7: Final test
    print("\n[6/6] Running final verification...")
    final_test = test_script()
    
    # Completion
    if final_test:
        print("\n✅ Post-Compaction Context Injector installed successfully!")
        print("\nThe system will now automatically detect and fix context compaction events.")
        print("You can also manually trigger a context injection with:")
        print(f"  python3 {SCRIPT_PATH} --inject-now --session [SESSION_ID]")
    else:
        print("\n⚠️ Installation completed with warnings.")
        print("Please check the log for details.")
    
    print("\nInstallation completed at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()