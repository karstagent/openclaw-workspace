#!/usr/bin/env python3
"""
Improved Heartbeat State Manager for OpenClaw
This script implements a rotating check system based on priority and last-checked times.
"""

import os
import json
import datetime
import time
from typing import Dict, Any, Optional

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
STATE_FILE = os.path.join(MEMORY_DIR, "heartbeat-state.json")

# Ensure memory directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)

class HeartbeatManager:
    """
    Manages the rotating heartbeat check system
    """
    def __init__(self):
        self.state = self._load_state()
        self.current_time = datetime.datetime.now()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from the state file, or create default state if it doesn't exist"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding {STATE_FILE}, using default state")
        
        # Default state
        return {
            "lastChecks": {
                "autonomousSystem": 0,
                "glasswall": 0,
                "platforms": 0,
                "deployment": 0,
                "memoryMaintenance": 0,
                "missionControl": 0,
                "commandStation": 0,
                "webSearch": 0,
                "apiHealth": 0
            },
            "checkFrequency": {
                "autonomousSystem": 1800,  # 30 minutes
                "glasswall": 3600,         # 1 hour
                "platforms": 14400,        # 4 hours
                "deployment": 7200,        # 2 hours
                "memoryMaintenance": 43200,# 12 hours
                "missionControl": 7200,    # 2 hours
                "commandStation": 7200,    # 2 hours
                "webSearch": 14400,        # 4 hours
                "apiHealth": 3600          # 1 hour
            },
            "timeWindows": {
                "webSearch": {"start": "09:00", "end": "23:00"},
                "platforms": {"start": "10:00", "end": "22:00"}
            },
            "nextTasks": {
                "progressUpdate": "2026-02-09 09:00:00",
                "weeklySummary": "2026-02-10 09:00:00"
            }
        }
    
    def _save_state(self) -> None:
        """Save the current state to the state file"""
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def _is_in_time_window(self, check_name: str) -> bool:
        """
        Check if the current time is within the allowed window for a check
        Returns True if no window is specified or current time is in window
        """
        if check_name not in self.state.get("timeWindows", {}):
            return True
        
        window = self.state["timeWindows"][check_name]
        now = self.current_time.strftime("%H:%M")
        
        return window["start"] <= now <= window["end"]
    
    def _calculate_priority_score(self, check_name: str) -> float:
        """
        Calculate priority score for a check based on how overdue it is
        Higher score means higher priority
        """
        last_check = self.state["lastChecks"].get(check_name, 0)
        frequency = self.state["checkFrequency"].get(check_name, 3600)
        
        # If never checked, give high priority but not maximum
        if last_check == 0:
            return 0.9
        
        time_since_check = time.time() - last_check
        overdue_ratio = time_since_check / frequency
        
        return overdue_ratio
    
    def determine_next_check(self) -> Optional[str]:
        """
        Determine which check should be run next
        Returns the name of the check, or None if nothing needs checking
        """
        highest_score = 0.0
        next_check = None
        
        for check_name in self.state["lastChecks"].keys():
            # Skip checks outside their time window
            if not self._is_in_time_window(check_name):
                continue
                
            score = self._calculate_priority_score(check_name)
            
            # Only consider checks that are at least 80% due
            if score >= 0.8 and score > highest_score:
                highest_score = score
                next_check = check_name
        
        return next_check
    
    def update_check_time(self, check_name: str) -> None:
        """Update the last check time for a specific check"""
        self.state["lastChecks"][check_name] = int(time.time())
        self._save_state()
    
    def get_check_info(self, check_name: str) -> Dict[str, Any]:
        """Get information about a specific check"""
        last_check = self.state["lastChecks"].get(check_name, 0)
        frequency = self.state["checkFrequency"].get(check_name, 3600)
        
        last_check_dt = datetime.datetime.fromtimestamp(last_check)
        next_check_dt = last_check_dt + datetime.timedelta(seconds=frequency)
        
        return {
            "name": check_name,
            "lastCheck": last_check_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "nextScheduledCheck": next_check_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "overdue": time.time() > last_check + frequency
        }
    
    def add_or_update_check(self, check_name: str, frequency_seconds: int, 
                           time_window: Optional[Dict[str, str]] = None) -> None:
        """Add a new check or update an existing one"""
        if check_name not in self.state["lastChecks"]:
            self.state["lastChecks"][check_name] = 0
        
        self.state["checkFrequency"][check_name] = frequency_seconds
        
        if time_window:
            if "timeWindows" not in self.state:
                self.state["timeWindows"] = {}
            self.state["timeWindows"][check_name] = time_window
        
        self._save_state()

def main():
    """Main function to demonstrate usage"""
    manager = HeartbeatManager()
    next_check = manager.determine_next_check()
    
    if next_check:
        print(f"Next check to run: {next_check}")
        check_info = manager.get_check_info(next_check)
        print(f"Last checked: {check_info['lastCheck']}")
        print(f"Next scheduled: {check_info['nextScheduledCheck']}")
        print(f"Is overdue: {check_info['overdue']}")
        
        # After running the check, update the time
        # manager.update_check_time(next_check)
    else:
        print("No checks need to be run at this time.")
    
    # Example of adding a new check
    # manager.add_or_update_check("newCheck", 3600, {"start": "09:00", "end": "17:00"})

if __name__ == "__main__":
    main()