#!/usr/bin/env python3
import json
import os
import sys
import time
from datetime import datetime
import urllib.request
import urllib.parse

# Load heartbeat state
def load_heartbeat_state():
    state_file = "/Users/karst/.openclaw/workspace/memory/heartbeat-state.json"
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading heartbeat state: {e}")
        return None

# Update heartbeat state
def update_heartbeat_state(check_name):
    state_file = "/Users/karst/.openclaw/workspace/memory/heartbeat-state.json"
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Update timestamp
        state["lastChecks"][check_name] = time.time()
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Updated heartbeat state for {check_name}")
    except Exception as e:
        print(f"Error updating heartbeat state: {e}")

# Check Vercel deployment status
def check_vercel_deployment():
    print("\n=== VERCEL DEPLOYMENT STATUS CHECK ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    vercel_token = os.environ.get("VERCEL_TOKEN", "")
    project_name = "glasswall-simple-app"  # Project name from vercel project ls
    
    # API endpoint
    base_url = "https://api.vercel.com"
    
    # Function to make API requests
    def make_request(url, params=None):
        headers = {
            "Authorization": f"Bearer {vercel_token}",
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
    
    # Get latest deployments
    url = f"{base_url}/v6/deployments"
    params = {
        "projectId": project_name,
        "limit": 5  # Get the 5 most recent deployments
    }
    
    response = make_request(url, params)
    
    if response.get("status_code") != 200 or "data" not in response:
        print(f"Error: {response.get('status_code')}")
        print(response.get("error", "Unknown error"))
        return False
    
    deployments_data = response["data"]
    
    if not deployments_data or "deployments" not in deployments_data:
        print("No deployments found")
        return False
    
    print(f"Found {len(deployments_data['deployments'])} recent deployments")
    
    # Check if we have any failing deployments
    failing_deployments = []
    
    for deployment in deployments_data['deployments']:
        deployment_id = deployment['uid']
        created_at = datetime.fromtimestamp(deployment['created'] / 1000)
        status = deployment['state']
        url = deployment.get('url', 'No URL available')
        
        print(f"\nDeployment: {deployment_id}")
        print(f"Created: {created_at}")
        print(f"Status: {status}")
        print(f"URL: https://{url}")
        
        if status != "READY":
            failing_deployments.append({
                "id": deployment_id,
                "created_at": created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "status": status,
                "url": url
            })
    
    # Save results to deployment status file
    status_file = "/Users/karst/.openclaw/workspace/memory/vercel_deployment_status.json"
    status_data = {
        "timestamp": time.time(),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.now().strftime('%H:%M:%S'),
        "project": project_name,
        "deployments": [
            {
                "id": d['uid'],
                "created_at": datetime.fromtimestamp(d['created'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "status": d['state'],
                "url": d.get('url', 'No URL available')
            } for d in deployments_data['deployments']
        ],
        "failing_deployments": failing_deployments
    }
    
    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        print(f"\nDeployment status saved to {status_file}")
    except Exception as e:
        print(f"Error saving deployment status: {e}")
    
    # Return True if there are no failing deployments
    return len(failing_deployments) == 0

if __name__ == "__main__":
    # Determine which check to run
    check_name = "deploymentStatus"
    
    # Run the deployment status check
    success = check_vercel_deployment()
    
    # Update heartbeat state
    update_heartbeat_state(check_name)
    
    # Exit with appropriate status code
    if success:
        sys.exit(0)
    else:
        sys.exit(1)