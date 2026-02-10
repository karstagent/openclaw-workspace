#!/usr/bin/env python3
import urllib.request
import urllib.parse
import os
import json
from datetime import datetime

# Configuration
VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN", "")  # Token should be provided via environment variable
PROJECT_NAME = "glasswall-simple-app"  # Correct project name from vercel project ls

# API endpoint
BASE_URL = "https://api.vercel.com"

def make_request(url, params=None):
    """Make a request to the Vercel API"""
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return {
                "status_code": response.status,
                "data": json.loads(response.read().decode("utf-8"))
            }
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "error": e.read().decode("utf-8")
        }

def get_latest_deployments():
    """Get the latest deployments for the project"""
    url = f"{BASE_URL}/v6/deployments"
    params = {
        "projectId": PROJECT_NAME,
        "limit": 5  # Get the 5 most recent deployments
    }
    
    response = make_request(url, params)
    
    if response.get("status_code") == 200:
        return response.get("data")
    else:
        print(f"Error: {response.get('status_code')}")
        print(response.get("error"))
        return None

def check_deployment_status(deployment_id):
    """Get details about a specific deployment"""
    url = f"{BASE_URL}/v13/deployments/{deployment_id}"
    
    response = make_request(url)
    
    if response.get("status_code") == 200:
        return response.get("data")
    else:
        print(f"Error: {response.get('status_code')}")
        print(response.get("error"))
        return None

def get_deployment_events(deployment_id):
    """Get build logs and events for a deployment"""
    url = f"{BASE_URL}/v3/deployments/{deployment_id}/events"
    
    response = make_request(url)
    
    if response.get("status_code") == 200:
        return response.get("data")
    else:
        print(f"Error: {response.get('status_code')}")
        print(response.get("error"))
        return None

def main():
    print("Checking Vercel deployment status for GlassWall project...")
    
    if not VERCEL_TOKEN:
        print("Error: VERCEL_TOKEN environment variable is not set")
        print("Please set your Vercel API token as an environment variable")
        return
    
    # Get latest deployments
    deployments = get_latest_deployments()
    
    if not deployments or "deployments" not in deployments:
        print("No deployments found or API error")
        return
    
    print(f"Found {len(deployments['deployments'])} recent deployments\n")
    
    for deployment in deployments['deployments']:
        deployment_id = deployment['uid']
        created_at = datetime.fromtimestamp(deployment['created'] / 1000)
        status = deployment['state']
        url = deployment.get('url', 'No URL available')
        
        print(f"Deployment: {deployment_id}")
        print(f"Created: {created_at}")
        print(f"Status: {status}")
        print(f"URL: https://{url}")
        
        if status == "ERROR":
            # Get deployment events to see error details
            events = get_deployment_events(deployment_id)
            if events:
                error_events = [e for e in events if e.get('type') == 'error']
                for error in error_events:
                    print(f"Error: {error.get('payload', {}).get('text', 'Unknown error')}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()