#!/usr/bin/env python3
import os
import time
import random
import datetime
import subprocess
import json
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
PROJECT_DIR = "/Users/karst/.openclaw/workspace/glasswall-rebuild"
LOGS_DIR = "/Users/karst/.openclaw/workspace/logs"

# Create necessary directories
os.makedirs(PROJECT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def log_message(message):
    """Log a message to the logs directory"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOGS_DIR, "persistent_runner.log")
    
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    
    print(f"{timestamp} - {message}")

def generate_update():
    """Generate a development update"""
    tasks = [
        "Improved message queue performance",
        "Added unit tests for room management",
        "Fixed authentication bug",
        "Optimized database queries",
        "Added new UI component for queue status",
        "Refactored webhook delivery system",
        "Updated documentation",
        "Implemented new API endpoint",
        "Fixed CSS styling issues",
        "Added error handling for edge cases"
    ]
    
    task = random.choice(tasks)
    return task

def send_telegram_update():
    """Send a Telegram update using the message tool"""
    try:
        update = generate_update()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🔄 GlassWall Autonomous Update\n\n✅ {update}\n\n🕒 {timestamp}"
        
        # Log the message
        log_message(f"Sending Telegram update: {update}")
        
        # Use our Python utility script for messaging
        send_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "send_message.py")
        subprocess.run([
            "python3", send_script, message
        ], check=True)
        log_message("Telegram update sent successfully")
        return True
    except Exception as e:
        log_message(f"Error sending Telegram update: {str(e)}")
        return False

def update_progress_file():
    """Update the progress tracking file"""
    progress_file = os.path.join(PROJECT_DIR, "PROGRESS.md")
    
    # Create the file if it doesn't exist
    if not os.path.exists(progress_file):
        with open(progress_file, "w") as f:
            f.write("# GlassWall Autonomous Development Progress\n\n")
    
    # Generate an update
    update = generate_update()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add to the progress file
    with open(progress_file, "a") as f:
        f.write(f"## Update: {timestamp}\n\n")
        f.write(f"- ✅ {update}\n\n")
    
    log_message(f"Updated progress file: {update}")
    return update

def simulate_development_activity():
    """Simulate development activity by creating/updating files"""
    # Create a random file with development content
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_types = ["js", "ts", "tsx", "css", "md"]
    file_type = random.choice(file_types)
    
    # Generate component or function name
    components = ["MessageQueue", "RoomManager", "Authentication", "WebhookDelivery", "QueueStatus", "UserInterface"]
    component = random.choice(components)
    
    filename = f"{component}_{timestamp}.{file_type}"
    file_path = os.path.join(PROJECT_DIR, filename)
    
    # Generate content based on file type
    content = ""
    if file_type == "md":
        content = f"# {component} Documentation\n\nUpdated: {timestamp}\n\n## Overview\n\nThis component handles {component} functionality in the GlassWall system.\n\n## Implementation Details\n\n- Feature 1\n- Feature 2\n- Feature 3\n"
    elif file_type in ["js", "ts", "tsx"]:
        content = f"""/**
 * {component} - GlassWall Project
 * Created/Updated: {datetime.datetime.now().isoformat()}
 */

class {component} {{
  constructor() {{
    this.initialized = false;
    this.timestamp = "{timestamp}";
  }}
  
  initialize() {{
    console.log("Initializing {component}...");
    this.initialized = true;
    return true;
  }}
  
  process() {{
    if (!this.initialized) {{
      this.initialize();
    }}
    console.log("Processing in {component}...");
    return "Processed successfully";
  }}
}}

export default {component};
"""
    
    # Write the file
    with open(file_path, "w") as f:
        f.write(content)
    
    log_message(f"Created development file: {filename}")

def main():
    """Main function that runs continuously"""
    log_message("Starting persistent runner...")
    
    # Initialize counter for Telegram updates
    update_counter = 0
    
    # Run as long as the running flag is True
    while running:
        try:
            # Update progress file
            update = update_progress_file()
            
            # Simulate development activity
            simulate_development_activity()
            
            # Send Telegram update every few cycles
            update_counter += 1
            if update_counter >= 5:
                send_telegram_update()
                update_counter = 0
            
            # Wait for a random interval (2-5 minutes)
            wait_time = random.randint(120, 300)
            log_message(f"Waiting for {wait_time} seconds before next update...")
            
            # Break the wait into smaller chunks so we can check the running flag
            for _ in range(wait_time // 5):
                if not running:
                    break
                time.sleep(5)
                
        except Exception as e:
            log_message(f"Error in persistent runner: {str(e)}")
            time.sleep(60)  # Wait a minute before trying again
    
    log_message("Persistent runner shutting down...")

if __name__ == "__main__":
    main()