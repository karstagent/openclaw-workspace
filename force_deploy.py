#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
from datetime import datetime

def log_message(message, level="INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def check_for_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(["vercel", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            log_message(f"Vercel CLI installed: {result.stdout.strip()}")
            return True
        else:
            log_message("Vercel CLI not found", "ERROR")
            return False
    except FileNotFoundError:
        log_message("Vercel CLI not installed", "ERROR")
        return False

def install_vercel_cli():
    """Install Vercel CLI"""
    log_message("Installing Vercel CLI...")
    try:
        result = subprocess.run(["npm", "install", "-g", "vercel"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            log_message("Successfully installed Vercel CLI")
            return True
        else:
            log_message(f"Failed to install Vercel CLI: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Error installing Vercel CLI: {str(e)}", "ERROR")
        return False

def trigger_deployment(project_path):
    """Trigger a new deployment on Vercel"""
    log_message(f"Triggering deployment for project at {project_path}")
    
    try:
        # Change to the project directory
        os.chdir(project_path)
        
        # Run the vercel deploy command with --prod flag for production deployment
        result = subprocess.run(["vercel", "deploy", "--prod"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode == 0:
            log_message("Deployment triggered successfully")
            log_message(f"Output: {result.stdout}")
            return True, result.stdout
        else:
            log_message(f"Failed to trigger deployment: {result.stderr}", "ERROR")
            return False, result.stderr
            
    except Exception as e:
        log_message(f"Error triggering deployment: {str(e)}", "ERROR")
        return False, str(e)

def main():
    """Main function"""
    log_message("=" * 60)
    log_message("Vercel Force Deployment Script")
    log_message(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 60)
    
    # Default project path
    project_path = "/Users/karst/.openclaw/workspace/glasswall-rebuild"
    
    # Allow override from command line
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    
    # Check if Vercel CLI is installed
    if not check_for_vercel_cli():
        log_message("Installing Vercel CLI...")
        if not install_vercel_cli():
            log_message("Failed to install Vercel CLI. Exiting.", "ERROR")
            sys.exit(1)
    
    # Trigger deployment
    success, message = trigger_deployment(project_path)
    
    # Log the result
    if success:
        log_message("Deployment process initiated successfully")
        log_message("Deployment URLs will be available in the Vercel dashboard")
        sys.exit(0)
    else:
        log_message(f"Deployment failed: {message}", "ERROR")
        log_message("Manual intervention may be required", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()