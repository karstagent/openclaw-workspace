#!/usr/bin/env python3
"""
Process Monitor Handler
This script is triggered by OpenClaw's cron scheduler to ensure background processes are running
"""

import os
import subprocess
import json
import datetime
import sys

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
LOGS_DIR = os.path.join(WORKSPACE, "logs")
SCRIPTS = ["persistent_runner.py", "github_sync.py", "monitor.py"]
STATUS_FILE = os.path.join(WORKSPACE, "autonomous_status.txt")
PYTHON_CMD = "python3"

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

def log_message(message):
    """Log a message to the logs directory"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOGS_DIR, "process_monitor_handler.log")
    
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    
    print(f"{timestamp} - {message}")

def is_script_running(script_name):
    """Check if a script is running using a reliable approach"""
    try:
        # Use pgrep for more reliable process checking
        result = subprocess.run(
            ["pgrep", "-f", script_name], 
            capture_output=True, 
            text=True
        )
        
        # If exit code is 0, process is running
        return result.returncode == 0
    except Exception as e:
        log_message(f"Error checking if {script_name} is running: {str(e)}")
        return False

def start_script(script_name):
    """Start a Python script"""
    try:
        script_path = os.path.join(WORKSPACE, script_name)
        log_message(f"Starting {script_name}...")
        
        # Make sure the script is executable
        subprocess.run(["chmod", "+x", script_path], check=True)
        
        # Start the script with nohup
        log_file = os.path.join(LOGS_DIR, f"{script_name}.log")
        with open(log_file, "a") as f:
            process = subprocess.Popen(
                ["nohup", PYTHON_CMD, script_path],
                stdout=f,
                stderr=f,
                preexec_fn=os.setpgrp,
                start_new_session=True
            )
        
        # Store the PID
        pid_file = os.path.join(WORKSPACE, f"{script_name}.pid")
        with open(pid_file, "w") as f:
            f.write(str(process.pid))
            
        log_message(f"Started {script_name} with PID {process.pid}")
        return True
    except Exception as e:
        log_message(f"Error starting {script_name}: {str(e)}")
        return False

def update_status_file():
    """Update the status file with current information"""
    try:
        status_content = [
            "Autonomous System Status",
            "-----------------------",
            f"Last checked: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Running processes:"
        ]
        
        for script_name in SCRIPTS:
            running = is_script_running(script_name)
            status = "✅ Running" if running else "❌ Not running"
            status_content.append(f"• {script_name}: {status}")
        
        with open(STATUS_FILE, "w") as f:
            f.write("\n".join(status_content))
            
        log_message("Updated status file")
        return True
    except Exception as e:
        log_message(f"Error updating status file: {str(e)}")
        return False

def send_notification(message):
    """Send a notification through OpenClaw"""
    try:
        # Use our Python utility script for messaging
        send_script = os.path.join(WORKSPACE, "send_message.py")
        subprocess.run([
            "python3", send_script, message
        ], check=True)
        log_message(f"Sent notification: {message}")
        return True
    except Exception as e:
        log_message(f"Error sending notification: {str(e)}")
        return False

def check_and_restart_processes():
    """Check if processes are running and restart if needed"""
    started = 0
    already_running = 0
    failed = 0
    
    for script_name in SCRIPTS:
        if is_script_running(script_name):
            log_message(f"{script_name} is already running")
            already_running += 1
        else:
            log_message(f"{script_name} is not running, attempting to start...")
            if start_script(script_name):
                started += 1
            else:
                failed += 1
    
    return started, already_running, failed

def main():
    """Main function"""
    log_message("Process Monitor Handler started")
    
    # Check and restart processes
    started, already_running, failed = check_and_restart_processes()
    
    # Update status file
    update_status_file()
    
    # Prepare notification message
    if started > 0 or failed > 0:
        status_message = "🔄 Autonomous System Status Update:\n\n"
        
        if started > 0:
            status_message += f"✅ Started {started} processes\n"
        
        if failed > 0:
            status_message += f"❌ Failed to start {failed} processes\n"
            
        status_message += f"✅ {already_running} processes already running\n\n"
        
        # Add details about each script
        status_message += "Current status:\n"
        for script_name in SCRIPTS:
            running = is_script_running(script_name)
            status = "✅ Running" if running else "❌ Not running"
            status_message += f"• {script_name}: {status}\n"
        
        # Send notification
        send_notification(status_message)
    else:
        log_message("All processes running, no notification needed")
    
    log_message("Process Monitor Handler completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())