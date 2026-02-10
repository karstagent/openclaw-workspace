#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime

def log_message(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def trigger_deploy_hook(hook_url):
    """
    Trigger a Vercel deployment using a deploy hook URL
    """
    if not hook_url or not hook_url.startswith("https://api.vercel.com"):
        log_message("Invalid deploy hook URL. Should start with https://api.vercel.com")
        return False, "Invalid URL format"
    
    log_message(f"Triggering deployment using hook: {hook_url}")
    
    try:
        # Send POST request to the deploy hook URL
        response = requests.post(hook_url)
        
        # Check if the request was successful
        if response.status_code == 201 or response.status_code == 200:
            log_message("Deploy hook triggered successfully!")
            log_message(f"Response: {response.text}")
            return True, response.text
        else:
            log_message(f"Failed to trigger deploy hook. Status code: {response.status_code}")
            log_message(f"Response: {response.text}")
            return False, f"Status code: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        log_message(f"Error triggering deploy hook: {str(e)}")
        return False, str(e)

def main():
    """Main function"""
    print("=" * 60)
    print("Vercel Deploy Hook Trigger")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python trigger_vercel_deploy_hook.py <deploy_hook_url>")
        print("Example: python trigger_vercel_deploy_hook.py https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy")
        sys.exit(1)
    
    # Get the deploy hook URL from command line arguments
    deploy_hook_url = sys.argv[1]
    
    # Trigger the deploy hook
    success, message = trigger_deploy_hook(deploy_hook_url)
    
    # Exit with appropriate code
    if success:
        print("Deploy hook triggered successfully!")
        sys.exit(0)
    else:
        print(f"Failed to trigger deploy hook: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()