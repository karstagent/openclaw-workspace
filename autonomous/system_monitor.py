#!/usr/bin/env python3
"""
System Monitor - Ensures the continuous runner is always running
Checks for deadlocks, hangs, and crashes and restarts processes as needed
"""

import os
import sys
import time
import signal
import logging
import subprocess
import json
import datetime
# Try to import psutil, but provide fallback if not available
try:
    import psutil
except ImportError:
    # Create a minimal psutil replacement for the required functionality
    class PsutilProcess:
        def __init__(self, pid):
            self.pid = pid
            self._cmdline = None
            
        def cmdline(self):
            if self._cmdline is None:
                try:
                    with open(f"/proc/{self.pid}/cmdline", 'r') as f:
                        self._cmdline = f.read().strip().split('\0')
                except FileNotFoundError:
                    # On macOS, use ps command
                    try:
                        import subprocess
                        result = subprocess.run(
                            ["ps", "-p", str(self.pid), "-o", "command="],
                            capture_output=True,
                            text=True
                        )
                        self._cmdline = result.stdout.strip().split()
                    except Exception:
                        self._cmdline = []
            return self._cmdline
    
    class PsutilModule:
        class NoSuchProcess(Exception):
            pass
            
        def Process(self, pid):
            # Check if process exists
            try:
                import os
                os.kill(pid, 0)  # Doesn't actually send a signal
                return PsutilProcess(pid)
            except ProcessLookupError:
                raise self.NoSuchProcess(f"No process with pid {pid}")
    
    psutil = PsutilModule()
from pathlib import Path

# Setup constants
WORKSPACE = Path("/Users/karst/.openclaw/workspace")
AUTONOMOUS_DIR = WORKSPACE / "autonomous"
LOGS_DIR = AUTONOMOUS_DIR / "logs"
RUNNER_PID_FILE = AUTONOMOUS_DIR / "continuous_runner.pid"
STATUS_FILE = AUTONOMOUS_DIR / "runner_status.json"
MONITOR_STATUS_FILE = AUTONOMOUS_DIR / "monitor_status.json"
CONTINUOUS_RUNNER_SCRIPT = AUTONOMOUS_DIR / "continuous_runner.py"
MONITOR_PID_FILE = AUTONOMOUS_DIR / "system_monitor.pid"

# Create necessary directories
AUTONOMOUS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "system_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemMonitor")

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
    with open(MONITOR_PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def update_status(status):
    """Update the monitor status file"""
    status_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "pid": os.getpid(),
        "status": status,
        "uptime": (datetime.datetime.now() - start_time).total_seconds()
    }
    
    with open(MONITOR_STATUS_FILE, 'w') as f:
        json.dump(status_data, f, indent=2)

def is_runner_running():
    """Check if the continuous runner is currently running"""
    if not RUNNER_PID_FILE.exists():
        logger.info("Runner PID file does not exist")
        return False
    
    try:
        with open(RUNNER_PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process is running
        process = psutil.Process(pid)
        
        # Check if it's the correct process (python running continuous_runner.py)
        cmd_line = " ".join(process.cmdline()).lower()
        if "python" in cmd_line and "continuous_runner.py" in cmd_line:
            return True
        
        logger.warning(f"Process {pid} is running but doesn't appear to be the runner (cmdline: {cmd_line})")
        return False
        
    except (ProcessLookupError, psutil.NoSuchProcess):
        logger.info(f"Process with PID {pid} does not exist")
        return False
    except ValueError:
        logger.error(f"Invalid PID in runner PID file")
        return False
    except Exception as e:
        logger.error(f"Error checking runner process: {e}")
        return False

def is_runner_healthy():
    """Check if the continuous runner is healthy (not hung/deadlocked)"""
    if not STATUS_FILE.exists():
        logger.warning("Runner status file does not exist")
        return False
    
    try:
        with open(STATUS_FILE, 'r') as f:
            status_data = json.load(f)
        
        # Check if status is too old (indicates a possible hang)
        timestamp = datetime.datetime.fromisoformat(status_data["timestamp"])
        now = datetime.datetime.now()
        
        # If status hasn't been updated in 10 minutes, consider it unhealthy
        if (now - timestamp).total_seconds() > 600:  # 10 minutes
            logger.warning(f"Runner status is too old: {status_data['timestamp']}")
            return False
        
        # Check the actual status
        if status_data["status"] in ["error", "too_many_failures", "shutdown"]:
            logger.warning(f"Runner status indicates a problem: {status_data['status']}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking runner status: {e}")
        return False

def start_runner():
    """Start the continuous runner process"""
    logger.info("Starting continuous runner...")
    
    try:
        # Start the runner as a detached process
        process = subprocess.Popen(
            [sys.executable, str(CONTINUOUS_RUNNER_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )
        
        logger.info(f"Started continuous runner with PID {process.pid}")
        
        # Wait a bit for it to initialize
        time.sleep(5)
        
        # Check if it's still running after initialization
        if is_runner_running():
            logger.info("Continuous runner started successfully")
            return True
        else:
            logger.error("Continuous runner failed to start")
            return False
        
    except Exception as e:
        logger.error(f"Error starting continuous runner: {e}")
        return False

def stop_runner():
    """Stop the continuous runner process"""
    if not RUNNER_PID_FILE.exists():
        logger.info("Runner PID file does not exist, nothing to stop")
        return True
    
    try:
        with open(RUNNER_PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        logger.info(f"Stopping continuous runner (PID: {pid})...")
        
        # Try to stop it gracefully first
        try:
            os.kill(pid, signal.SIGTERM)
            
            # Wait for it to stop (up to 10 seconds)
            for _ in range(10):
                if not is_runner_running():
                    logger.info("Continuous runner stopped successfully")
                    return True
                time.sleep(1)
            
            # Force kill if it didn't stop gracefully
            logger.warning("Continuous runner didn't stop gracefully, force killing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(2)
            
            if not is_runner_running():
                logger.info("Continuous runner force killed successfully")
                return True
            else:
                logger.error("Failed to kill continuous runner")
                return False
                
        except ProcessLookupError:
            logger.info("Process already gone")
            # Remove the PID file if it still exists
            if RUNNER_PID_FILE.exists():
                RUNNER_PID_FILE.unlink()
            return True
            
    except Exception as e:
        logger.error(f"Error stopping continuous runner: {e}")
        return False

def restart_runner():
    """Restart the continuous runner"""
    logger.info("Restarting continuous runner...")
    
    stop_runner()
    
    # Slight delay to ensure proper shutdown
    time.sleep(3)
    
    return start_runner()

def main():
    global start_time
    start_time = datetime.datetime.now()
    
    logger.info("Starting system monitor...")
    write_pid_file()
    update_status("starting")
    
    # Check if runner is already running
    if not is_runner_running():
        logger.info("Continuous runner is not running, starting it...")
        start_runner()
    else:
        logger.info("Continuous runner is already running")
    
    # Main monitoring loop
    check_interval = 60  # Check every minute
    
    while running:
        try:
            update_status("monitoring")
            
            # Check if runner is running
            if not is_runner_running():
                logger.warning("Continuous runner is not running, restarting...")
                start_runner()
            # Check if runner is healthy
            elif not is_runner_healthy():
                logger.warning("Continuous runner is not healthy, restarting...")
                restart_runner()
            else:
                logger.info("Continuous runner is running and healthy")
                update_status("idle")
            
            # Sleep in small chunks to respond to shutdown signals
            for _ in range(check_interval):
                if not running:
                    break
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(check_interval)
    
    # Clean shutdown
    logger.info("System monitor shutting down...")
    update_status("shutdown")
    
    # Remove PID file
    if MONITOR_PID_FILE.exists():
        MONITOR_PID_FILE.unlink()
        
    logger.info("Shutdown complete")

if __name__ == "__main__":
    main()