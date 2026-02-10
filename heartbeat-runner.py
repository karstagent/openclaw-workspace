#!/usr/bin/env python3

import json
import os
import datetime
import time
import subprocess
import sys

# Path to the heartbeat state file
STATE_FILE = "/Users/karst/.openclaw/workspace/memory/heartbeat-state.json"

def load_state():
    """Load the heartbeat state from file"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create a default state file if it doesn't exist
        default_state = {
            "lastChecks": {},
            "checkPriorities": {},
            "checkIntervals": {},
            "timeWindows": {}
        }
        save_state(default_state)
        return default_state

def save_state(state):
    """Save the heartbeat state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_check_due(check_name, state):
    """Check if a specific heartbeat check is due to run"""
    now = time.time()
    last_check = state["lastChecks"].get(check_name, 0)
    interval = state["checkIntervals"].get(check_name, 3600)  # Default to 1 hour
    
    # Check time window
    current_hour = datetime.datetime.now().hour
    time_window = state["timeWindows"].get(check_name, {"start": 0, "end": 24})
    
    if not (time_window["start"] <= current_hour < time_window["end"]):
        return False  # Outside time window
    
    # Check if enough time has passed since the last check
    return (now - last_check) >= interval

def get_next_check(state):
    """Determine the highest priority check that is due to run"""
    # Sort checks by priority (highest first)
    checks = sorted(
        state["checkPriorities"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Find the highest priority check that is due
    for check_name, priority in checks:
        if is_check_due(check_name, state):
            return check_name
    
    return None  # No checks are due

def update_check_timestamp(check_name, state):
    """Update the timestamp for a completed check"""
    state["lastChecks"][check_name] = time.time()
    save_state(state)

def run_check(check_name):
    """Run a specific heartbeat check"""
    print(f"Running heartbeat check: {check_name}")
    
    if check_name == "kanban":
        result = subprocess.run(
            ["/Users/karst/.openclaw/workspace/kanban-heartbeat-handler.py"],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        if output != "HEARTBEAT_OK":
            print(f"Kanban check result: {output}")
        return result.returncode == 0
        
    elif check_name == "systemHealth":
        result = subprocess.run(
            ["python3", "/Users/karst/.openclaw/workspace/process_monitor_handler.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
        
    # Add other checks as needed...
    
    print(f"No implementation for check: {check_name}")
    return False

def main():
    # Load the current state
    state = load_state()
    
    # Get the next check to run
    check_name = get_next_check(state)
    
    if check_name:
        print(f"Running check: {check_name}")
        success = run_check(check_name)
        
        if success:
            update_check_timestamp(check_name, state)
            print(f"Successfully completed check: {check_name}")
        else:
            print(f"Check failed: {check_name}")
    else:
        print("No checks are due at this time")

if __name__ == "__main__":
    main()