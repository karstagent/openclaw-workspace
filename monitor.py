#!/usr/bin/env python3
import os
import subprocess
import time
import datetime
import signal
import sys

# Setup signal handlers for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    print(f"Received signal {sig}, shutting down gracefully...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Constants
LOGS_DIR = "/Users/karst/.openclaw/workspace/logs"
PYTHON_PATH = "python3"  # Use system PATH to find python
SCRIPTS = [
    "/Users/karst/.openclaw/workspace/persistent_runner.py",
    "/Users/karst/.openclaw/workspace/github_sync.py"
]
CHECK_INTERVAL = 300  # Check every 5 minutes
STATUS_FILE = "/Users/karst/.openclaw/workspace/monitor_status.json"

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

def log_message(message):
    """Log a message to the logs directory"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOGS_DIR, "monitor.log")
    
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    
    print(f"{timestamp} - {message}")

def is_script_running(script_path):
    """Check if a script is running using a more robust approach"""
    try:
        # Get the basename of the script
        script_name = os.path.basename(script_path)
        
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

def restart_script(script_path):
    """Restart a script with proper detachment"""
    try:
        script_name = os.path.basename(script_path)
        log_message(f"Restarting {script_name}...")
        
        # Make sure the script is executable
        subprocess.run(["chmod", "+x", script_path], check=True)
        
        # Start the script with nohup to ensure it stays running
        log_file = os.path.join(LOGS_DIR, f"{script_name}.log")
        with open(log_file, "a") as f:
            process = subprocess.Popen(
                ["nohup", PYTHON_PATH, script_path],
                stdout=f,
                stderr=f,
                # Detach the process completely
                preexec_fn=os.setpgrp,
                start_new_session=True
            )
        
        log_message(f"Restarted {script_name} with PID {process.pid}")
        return True
    except Exception as e:
        log_message(f"Error restarting {script_name}: {str(e)}")
        return False

def update_status_file(status):
    """Update the status file with the current state"""
    try:
        import json
        timestamp = datetime.datetime.now().isoformat()
        
        status_data = {
            "timestamp": timestamp,
            "status": status,
            "scripts": {}
        }
        
        for script_path in SCRIPTS:
            script_name = os.path.basename(script_path)
            is_running = is_script_running(script_path)
            status_data["scripts"][script_name] = {
                "running": is_running,
                "path": script_path
            }
        
        with open(STATUS_FILE, "w") as f:
            json.dump(status_data, f, indent=2)
        
        return True
    except Exception as e:
        log_message(f"Error updating status file: {str(e)}")
        return False

def notify_openclaw(message):
    """Send a notification through OpenClaw"""
    try:
        # Use our Python utility script for messaging
        send_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "send_message.py")
        subprocess.run([
            "python3", send_script, message
        ], check=True)
        log_message(f"Sent notification: {message}")
        return True
    except Exception as e:
        log_message(f"Error sending notification: {str(e)}")
        return False

def main():
    """Main monitoring loop"""
    log_message("Starting monitoring process")
    notify_openclaw("🔄 Autonomous Monitor: Starting background process monitoring")
    
    # Initialize failure counters
    failures = {script: 0 for script in SCRIPTS}
    
    # Set up last check time
    last_check_time = time.time()
    
    # Run as long as the running flag is True
    while running:
        try:
            current_time = time.time()
            
            # Check if the appropriate interval has passed
            if current_time - last_check_time >= CHECK_INTERVAL:
                log_message("Performing script check...")
                
                # Check each script
                restart_count = 0
                for script_path in SCRIPTS:
                    script_name = os.path.basename(script_path)
                    
                    # Check if the script is running
                    if not is_script_running(script_path):
                        failures[script_path] += 1
                        log_message(f"{script_name} is not running (failure #{failures[script_path]}), restarting...")
                        
                        # Restart the script
                        if restart_script(script_path):
                            restart_count += 1
                            
                            # Notify if multiple failures
                            if failures[script_path] >= 3:
                                notify_openclaw(f"⚠️ Autonomous Monitor: {script_name} has failed {failures[script_path]} times and was restarted.")
                        else:
                            log_message(f"Failed to restart {script_name}")
                    else:
                        log_message(f"{script_name} is running normally")
                        failures[script_path] = 0
                
                # Update the status file
                update_status_file("active")
                
                # Report on actions taken
                if restart_count > 0:
                    log_message(f"Restarted {restart_count} scripts")
                else:
                    log_message("All scripts running normally")
                
                # Update last check time
                last_check_time = current_time
                
                # Send daily status if around midnight
                now = datetime.datetime.now()
                if now.hour == 0 and now.minute < 5:
                    # It's around midnight, send a daily status
                    status_message = "🔄 Daily Autonomous Monitor Status:\n\n"
                    for script_path in SCRIPTS:
                        script_name = os.path.basename(script_path)
                        status = "✅ Running" if is_script_running(script_path) else "❌ Stopped"
                        status_message += f"• {script_name}: {status}\n"
                    
                    notify_openclaw(status_message)
            
            # Short sleep to check for signals
            time.sleep(5)
            
        except Exception as e:
            log_message(f"Error in monitoring process: {str(e)}")
            time.sleep(60)  # Wait a minute before trying again
    
    # Update status when shutting down
    update_status_file("stopped")
    log_message("Monitoring process shutting down...")
    notify_openclaw("⚠️ Autonomous Monitor: Background monitoring process has stopped")

if __name__ == "__main__":
    main()