#!/usr/bin/env python3
"""
Continuous Runner - Keeps the task manager running continuously
Handles error recovery, logging, and status reporting
"""

import os
import sys
import time
import signal
import logging
import subprocess
import json
import datetime
import random
from pathlib import Path

# Setup constants
WORKSPACE = Path("/Users/karst/.openclaw/workspace")
AUTONOMOUS_DIR = WORKSPACE / "autonomous"
LOGS_DIR = AUTONOMOUS_DIR / "logs"
PID_FILE = AUTONOMOUS_DIR / "continuous_runner.pid"
STATUS_FILE = AUTONOMOUS_DIR / "runner_status.json"
TASK_MANAGER_SCRIPT = AUTONOMOUS_DIR / "task_manager.py"

# Create necessary directories
AUTONOMOUS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "continuous_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ContinuousRunner")

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def write_pid_file():
    """Write PID to file"""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def update_status(status):
    """Update the runner status file"""
    status_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "pid": os.getpid(),
        "status": status,
        "uptime": (datetime.datetime.now() - start_time).total_seconds()
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f, indent=2)

def run_task_manager():
    """Run a single iteration of the task manager"""
    try:
        logger.info("Running task manager...")
        update_status("running_task_manager")
        
        result = subprocess.run(
            [sys.executable, str(TASK_MANAGER_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Task manager failed with exit code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            update_status("task_manager_error")
            return False
        
        logger.info("Task manager completed successfully")
        update_status("idle")
        return True
        
    except Exception as e:
        logger.error(f"Error running task manager: {e}")
        update_status("error")
        return False

def get_next_run_interval():
    """Get a random interval for the next run"""
    # Task processing happens at a variable rate to make it more natural
    # and prevent API rate limiting issues
    base_interval = 60  # One minute base
    jitter = random.randint(0, 120)  # Up to 2 minutes of jitter
    return base_interval + jitter

def main():
    global start_time
    start_time = datetime.datetime.now()
    
    logger.info("Starting continuous runner...")
    write_pid_file()
    update_status("starting")
    
    # Initial delay to let the system settle
    time.sleep(5)
    
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    while running:
        try:
            success = run_task_manager()
            
            if success:
                consecutive_failures = 0
                
                # Get the interval until next run
                interval = get_next_run_interval()
                logger.info(f"Waiting {interval} seconds until next task manager run")
                
                # Wait in small chunks so we can respond to shutdown signals quickly
                for _ in range(interval):
                    if not running:
                        break
                    time.sleep(1)
            else:
                consecutive_failures += 1
                logger.warning(f"Task manager failed, consecutive failures: {consecutive_failures}")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"Too many consecutive failures ({consecutive_failures}), exiting")
                    update_status("too_many_failures")
                    break
                
                # Wait before retrying (with exponential backoff)
                retry_delay = min(30 * (2 ** (consecutive_failures - 1)), 300)
                logger.info(f"Waiting {retry_delay} seconds before retrying")
                
                # Wait in small chunks so we can respond to shutdown signals quickly
                for _ in range(retry_delay):
                    if not running:
                        break
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            consecutive_failures += 1
            
            if consecutive_failures >= max_consecutive_failures:
                logger.error(f"Too many consecutive failures ({consecutive_failures}), exiting")
                update_status("too_many_failures")
                break
            
            # Wait before retrying
            time.sleep(30)
    
    # Clean shutdown
    logger.info("Continuous runner shutting down...")
    update_status("shutdown")
    
    # Remove PID file
    if PID_FILE.exists():
        PID_FILE.unlink()
        
    logger.info("Shutdown complete")

if __name__ == "__main__":
    main()