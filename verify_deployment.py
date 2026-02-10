#!/usr/bin/env python3
import os
import sys
import time
import requests
import json
from datetime import datetime

def check_vercel_deployment(project_name="glasswall-rebuild-karsts-pr"):
    """
    Check the status of a Vercel deployment
    Returns: (success, message)
    """
    print(f"Checking deployment status for {project_name}...")
    
    try:
        # First try to access the site directly
        url = f"https://{project_name}.vercel.app"
        print(f"Testing access to: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Deployment accessible (Status {response.status_code})")
            return True, f"Deployment is live and accessible at {url}"
        else:
            print(f"⚠️ Deployment returned status code {response.status_code}")
            return False, f"Deployment returned unexpected status: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error accessing deployment: {str(e)}")
        return False, f"Deployment not accessible: {str(e)}"

def log_result(success, message):
    """Log the result to a file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = "/Users/karst/.openclaw/workspace/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/deployment_checks.log"
    
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {'SUCCESS' if success else 'FAILURE'}: {message}\n")
    
    print(f"📝 Results logged to {log_file}")

def main():
    print("=" * 50)
    print(f"Vercel Deployment Verification")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Default project to check
    project = "glasswall-rebuild-karsts-pr"
    
    # Allow override from command line
    if len(sys.argv) > 1:
        project = sys.argv[1]
    
    # Do the check
    success, message = check_vercel_deployment(project)
    
    # Log the result
    log_result(success, message)
    
    # Set return code based on success
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()