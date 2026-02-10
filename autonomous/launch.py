#!/usr/bin/env python3
"""
Autonomous System Launcher
Starts the entire autonomous system and configures cron jobs for persistence
"""

import os
import sys
import subprocess
import time
import json
import datetime
import argparse
import logging
from pathlib import Path

# Setup constants
WORKSPACE = Path("/Users/karst/.openclaw/workspace")
AUTONOMOUS_DIR = WORKSPACE / "autonomous"
LOGS_DIR = AUTONOMOUS_DIR / "logs"
SYSTEM_MONITOR_SCRIPT = AUTONOMOUS_DIR / "system_monitor.py"
TASK_MANAGER_SCRIPT = AUTONOMOUS_DIR / "task_manager.py"
CONTINUOUS_RUNNER_SCRIPT = AUTONOMOUS_DIR / "continuous_runner.py"

# Create necessary directories
AUTONOMOUS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Launcher")

def setup_cron_jobs():
    """Set up cron jobs to ensure system persistence"""
    logger.info("Setting up cron jobs...")
    
    try:
        # Get the current cron jobs
        result = subprocess.run(
            ["openclaw", "cron", "action=list"],
            capture_output=True,
            text=True
        )
        
        if "missing required parameter" in result.stderr:
            # Handle the case where parameters need to be in JSON format
            result = subprocess.run(
                ["openclaw", "cron"],
                input='{"action":"list"}',
                capture_output=True,
                text=True
            )
        
        # Check if our monitor job already exists
        if "autonomous_monitor" in result.stdout:
            logger.info("Cron job already exists, no need to create")
            return True
        
        # Create a cron job to run every 5 minutes
        monitor_cron_job = {
            "action": "add",
            "job": {
                "name": "autonomous_monitor",
                "schedule": {
                    "kind": "cron",
                    "expr": "*/5 * * * *",  # Every 5 minutes
                    "tz": "America/Los_Angeles"
                },
                "payload": {
                    "kind": "systemEvent",
                    "text": f"Running system monitor check. Executing: python3 {SYSTEM_MONITOR_SCRIPT}"
                },
                "sessionTarget": "main",
                "enabled": True
            }
        }
        
        # Add the cron job
        result = subprocess.run(
            ["openclaw", "cron"],
            input=json.dumps(monitor_cron_job),
            capture_output=True,
            text=True
        )
        
        if "error" in result.stderr.lower():
            logger.error(f"Failed to create cron job: {result.stderr}")
            return False
            
        logger.info("Cron job created successfully")
        
        # Create hourly task execution cron job
        task_cron_job = {
            "action": "add",
            "job": {
                "name": "autonomous_task_execution",
                "schedule": {
                    "kind": "cron",
                    "expr": "0 * * * *",  # Every hour
                    "tz": "America/Los_Angeles"
                },
                "payload": {
                    "kind": "systemEvent",
                    "text": f"Running autonomous task execution. Executing: python3 {TASK_MANAGER_SCRIPT}"
                },
                "sessionTarget": "main",
                "enabled": True
            }
        }
        
        # Add the task cron job
        result = subprocess.run(
            ["openclaw", "cron"],
            input=json.dumps(task_cron_job),
            capture_output=True,
            text=True
        )
        
        if "error" in result.stderr.lower():
            logger.error(f"Failed to create task cron job: {result.stderr}")
            return False
            
        logger.info("Task cron job created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up cron jobs: {e}")
        return False

def start_system_monitor():
    """Start the system monitor process"""
    logger.info("Starting system monitor...")
    
    try:
        # Check if already running by running the system monitor script directly
        # This is handled internally by the script
        process = subprocess.Popen(
            [sys.executable, str(SYSTEM_MONITOR_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )
        
        logger.info(f"System monitor started with PID {process.pid}")
        
        # Wait a bit to ensure it starts properly
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"Error starting system monitor: {e}")
        return False

def verify_installation():
    """Verify that all required scripts are present and executable"""
    logger.info("Verifying installation...")
    
    required_files = [
        SYSTEM_MONITOR_SCRIPT,
        TASK_MANAGER_SCRIPT,
        CONTINUOUS_RUNNER_SCRIPT
    ]
    
    for file in required_files:
        if not file.exists():
            logger.error(f"Required file {file} does not exist")
            return False
        
        # Make it executable
        os.chmod(file, 0o755)
    
    logger.info("All required files present and executable")
    return True

def create_startup_script():
    """Create a startup script that can be run on boot"""
    logger.info("Creating startup script...")
    
    startup_script_path = AUTONOMOUS_DIR / "startup.sh"
    
    script_content = f"""#!/bin/bash
# Autonomous System Startup Script
# Run this script to start the autonomous system
# Can be added to system startup

echo "Starting autonomous system at $(date)"

# Change to the script directory
cd {AUTONOMOUS_DIR}

# Start the system monitor
python3 {SYSTEM_MONITOR_SCRIPT} &

echo "System monitor started with PID $!"
echo "Autonomous system startup complete"
"""
    
    with open(startup_script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(startup_script_path, 0o755)
    
    logger.info(f"Startup script created at {startup_script_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Launch the autonomous system")
    parser.add_argument("--no-cron", action="store_true", help="Don't set up cron jobs")
    parser.add_argument("--no-startup", action="store_true", help="Don't create startup script")
    args = parser.parse_args()
    
    logger.info("Launching autonomous system...")
    
    # Verify installation
    if not verify_installation():
        logger.error("Installation verification failed")
        return False
    
    # Set up cron jobs if not disabled
    if not args.no_cron:
        if not setup_cron_jobs():
            logger.warning("Failed to set up cron jobs, continuing anyway")
    
    # Create startup script if not disabled
    if not args.no_startup:
        if not create_startup_script():
            logger.warning("Failed to create startup script, continuing anyway")
    
    # Start the system monitor
    if not start_system_monitor():
        logger.error("Failed to start system monitor")
        return False
    
    logger.info("Autonomous system launched successfully")
    
    # Write launch details to a file
    launch_details = {
        "launched_at": datetime.datetime.now().isoformat(),
        "launched_by": os.environ.get("USER", "unknown"),
        "version": "1.0.0",
        "cron_jobs_enabled": not args.no_cron,
        "startup_script_created": not args.no_startup
    }
    
    with open(AUTONOMOUS_DIR / "launch_details.json", 'w') as f:
        json.dump(launch_details, f, indent=2)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)