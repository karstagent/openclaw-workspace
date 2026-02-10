#!/usr/bin/env python3
"""
Cron Job Manager for OpenClaw
Helps set up and manage cron jobs for the autonomous system.
"""

import os
import subprocess
import json
import argparse
import sys
import datetime
from typing import List, Dict, Any, Optional

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
LOGS_DIR = os.path.join(WORKSPACE, "logs")

def setup_cron_jobs() -> None:
    """
    Set up all required cron jobs for autonomous operation
    """
    # List of cron jobs to set up
    cron_jobs = [
        {
            "name": "Daily Progress Report",
            "schedule": "0 9 * * *",
            "timezone": "America/Los_Angeles",
            "session_type": "isolated",
            "message": "Generate a daily progress report covering: 1) GlassWall development status 2) Mission Control functionality 3) Any open issues or blockers 4) Plan for today",
            "model": "sonnet",
            "thinking": "medium",
            "announce": True
        },
        {
            "name": "API Health Check",
            "schedule": "0 */3 * * *",  # Every 3 hours
            "timezone": "America/Los_Angeles",
            "session_type": "isolated",
            "message": "Run a comprehensive health check of all APIs by executing the API health monitor script. Report any issues and recommend actions if services are down.",
            "model": "haiku",
            "thinking": "low",
            "announce": True
        },
        {
            "name": "Memory Maintenance",
            "schedule": "0 2 * * *",  # Every day at 2 AM
            "timezone": "America/Los_Angeles",
            "session_type": "isolated",
            "message": "Perform memory maintenance: Review recent daily memory files, update MEMORY.md with important information, and clean up any temporary files.",
            "model": "haiku", 
            "thinking": "low",
            "announce": False  # This is a background task that doesn't need announcements
        },
        {
            "name": "Weekly Summary",
            "schedule": "0 9 * * 1",  # Every Monday at 9 AM
            "timezone": "America/Los_Angeles",
            "session_type": "isolated",
            "message": "Create a comprehensive weekly summary with: 1) Major accomplishments 2) GlassWall development progress 3) Challenges and solutions 4) Goals for the coming week",
            "model": "sonnet",
            "thinking": "high",
            "announce": True
        },
        {
            "name": "Platform Research Update",
            "schedule": "0 11 * * 2,5",  # Tuesday and Friday at 11 AM
            "timezone": "America/Los_Angeles",
            "session_type": "isolated",
            "message": "Research and summarize updates on OpenClaw agent platforms. Look for new developments, integration patterns, and architectural improvements that could be applied to our systems.",
            "model": "sonnet",
            "thinking": "medium",
            "announce": True
        }
    ]
    
    # Set up each cron job
    for job in cron_jobs:
        setup_cron_job(job)

def setup_cron_job(job: Dict[str, Any]) -> None:
    """
    Set up a single cron job
    """
    print(f"Setting up cron job: {job['name']}")
    
    # Build the openclaw cron add command
    cmd = [
        "openclaw", "cron", "add",
        "--name", job["name"],
        "--cron", job["schedule"],
        "--tz", job["timezone"],
        "--session", job["session_type"],
        "--message", job["message"]
    ]
    
    # Add model if specified
    if "model" in job:
        cmd.extend(["--model", job["model"]])
    
    # Add thinking level if specified
    if "thinking" in job:
        cmd.extend(["--thinking", job["thinking"]])
    
    # Add announcement settings
    if job.get("announce", False):
        cmd.append("--announce")
        
        # Add channel if specified
        if "channel" in job:
            cmd.extend(["--channel", job["channel"]])
        
        # Add target if specified
        if "to" in job:
            cmd.extend(["--to", job["to"]])
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully set up cron job: {job['name']}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error setting up cron job {job['name']}: {e}")
        print(f"Error output: {e.stderr}")

def list_cron_jobs() -> None:
    """
    List all configured cron jobs
    """
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Configured cron jobs:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error listing cron jobs: {e}")
        print(f"Error output: {e.stderr}")

def remove_all_cron_jobs() -> None:
    """
    Remove all configured cron jobs
    WARNING: This will remove all cron jobs
    """
    try:
        # First list all jobs to get their IDs
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            check=True,
            capture_output=True,
            text=True
        )
        
        jobs = json.loads(result.stdout)
        
        if not jobs:
            print("No cron jobs to remove.")
            return
        
        for job in jobs:
            job_id = job.get("jobId") or job.get("id")
            job_name = job.get("name", "unnamed")
            
            if job_id:
                print(f"Removing cron job: {job_name} (ID: {job_id})")
                
                try:
                    remove_result = subprocess.run(
                        ["openclaw", "cron", "remove", job_id],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(f"Successfully removed cron job: {job_name}")
                except subprocess.CalledProcessError as e:
                    print(f"Error removing cron job {job_name}: {e}")
                    print(f"Error output: {e.stderr}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error listing cron jobs: {e}")
        print(f"Error output: {e.stderr}")
    except json.JSONDecodeError as e:
        print(f"Error parsing cron jobs list: {e}")

def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(description="Manage cron jobs for OpenClaw")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up cron jobs")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List configured cron jobs")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove-all", help="Remove all cron jobs")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_cron_jobs()
    elif args.command == "list":
        list_cron_jobs()
    elif args.command == "remove-all":
        remove_all_cron_jobs()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()