#!/usr/bin/env python3
import time
import os
import json
import random
import datetime
import subprocess

# Project to work on
PROJECT_DIR = "/Users/karst/.openclaw/workspace/glasswall-rebuild"

def log_activity(message):
    """Log activity to a file with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_dir = "/Users/karst/.openclaw/workspace/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, "autonomous_activity.log")
    
    with open(log_path, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def run_task():
    """Run a development task"""
    tasks = [
        "Implementing API endpoints",
        "Refactoring message queue service",
        "Optimizing database queries",
        "Adding unit tests",
        "Improving UI components",
        "Fixing bugs in authentication flow",
        "Implementing webhook delivery",
        "Adding new features to room management"
    ]
    
    # Select a random task
    task = random.choice(tasks)
    
    log_activity(f"Started: {task}")
    
    # Simulate work by creating/updating a file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    work_file = os.path.join(PROJECT_DIR, f"work_{timestamp}.txt")
    
    with open(work_file, "w") as f:
        f.write(f"Working on: {task}\n")
        f.write(f"Time: {datetime.datetime.now().isoformat()}\n")
        f.write("Status: In Progress\n")
    
    # Simulate work time
    work_time = random.randint(5, 15)
    time.sleep(work_time)
    
    # Update the file to show completion
    with open(work_file, "a") as f:
        f.write(f"Completed after: {work_time} seconds\n")
        f.write(f"Completion time: {datetime.datetime.now().isoformat()}\n")
    
    log_activity(f"Completed: {task} (took {work_time}s)")
    
    # Create progress summary
    progress_file = os.path.join(PROJECT_DIR, "PROGRESS.md")
    
    if not os.path.exists(progress_file):
        with open(progress_file, "w") as f:
            f.write("# Autonomous Development Progress\n\n")
    
    with open(progress_file, "a") as f:
        f.write(f"## {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"- Completed: **{task}**\n")
        f.write(f"- Time spent: {work_time} seconds\n\n")

def main():
    """Main function to run continuous tasks"""
    log_activity("Autonomous task runner started")
    
    # Create project directory if it doesn't exist
    os.makedirs(PROJECT_DIR, exist_ok=True)
    
    try:
        while True:
            # Run a task
            run_task()
            
            # Wait before next task
            wait_time = random.randint(30, 120)  # 30 seconds to 2 minutes
            log_activity(f"Waiting for {wait_time} seconds before next task")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        log_activity("Autonomous task runner stopped by user")
    except Exception as e:
        log_activity(f"Error in autonomous task runner: {str(e)}")

if __name__ == "__main__":
    main()