#!/Users/karst/.openclaw/workspace/venv/bin/python
"""
Heartbeat Runner for OpenClaw
This script runs during heartbeat checks and determines what to run
based on priority and timing.
"""

import os
import sys
import json
import datetime
import time
import subprocess
import logging
from typing import Dict, Any, Optional, List

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
STATE_FILE = os.path.join(MEMORY_DIR, "heartbeat-state.json")
LOGS_DIR = os.path.join(WORKSPACE, "logs")
RUNNER_LOG = os.path.join(LOGS_DIR, "heartbeat_runner.log")
AUTONOMOUS_DIR = os.path.join(WORKSPACE, "autonomous")

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=RUNNER_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Check runners for each type of heartbeat check
CHECK_RUNNERS = {
    "autonomousSystem": {
        "command": [sys.executable, os.path.join(WORKSPACE, "check_messages.py")],
        "model": "haiku",
        "thinking": "low"
    },
    "glasswall": {
        "command": [sys.executable, os.path.join(WORKSPACE, "dev_workflow.py"), "--status-check"],
        "model": "sonnet",
        "thinking": "medium"
    },
    "platforms": {
        "command": ["bash", "-c", f"cd {WORKSPACE} && python3 agent-platforms-research.py --mode=scan"],
        "model": "sonnet", 
        "thinking": "medium"
    },
    "deployment": {
        "command": ["bash", "-c", f"cd {WORKSPACE}/glasswall-rebuild && python3 check_deployment.py"],
        "model": "haiku",
        "thinking": "low"
    },
    "memoryMaintenance": {
        "command": [sys.executable, os.path.join(AUTONOMOUS_DIR, "memory_manager.py")],
        "model": "haiku",
        "thinking": "low"
    },
    "missionControl": {
        "command": [sys.executable, os.path.join(WORKSPACE, "check_mission_control_fixed.sh")],
        "model": "haiku",
        "thinking": "low"
    },
    "commandStation": {
        "command": ["bash", os.path.join(WORKSPACE, "check_mission_control.sh")],
        "model": "haiku",
        "thinking": "low"
    },
    "webSearch": {
        "command": ["openclaw", "eval", "web_search({ query: \"OpenClaw latest updates or news\" })"],
        "model": "haiku",
        "thinking": "low"
    },
    "apiHealth": {
        "command": [sys.executable, os.path.join(AUTONOMOUS_DIR, "api_health_monitor.py")],
        "model": "haiku",
        "thinking": "low"
    }
}

class HeartbeatRunner:
    """
    Runs heartbeat checks based on priority
    """
    def __init__(self):
        self.state = self._load_state()
        self.current_time = datetime.datetime.now()
        self.response = None
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from the state file, or create default state if it doesn't exist"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error(f"Error decoding {STATE_FILE}, using default state")
        
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
    
    def run_check(self, check_name: str) -> bool:
        """
        Run a specific check
        Returns True if the check ran successfully
        """
        if check_name not in CHECK_RUNNERS:
            logging.error(f"No runner configured for check: {check_name}")
            return False
        
        runner = CHECK_RUNNERS[check_name]
        command = runner["command"]
        
        logging.info(f"Running check: {check_name} with command: {' '.join(command)}")
        
        try:
            # Run the command
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Log the output
            logging.info(f"Check {check_name} completed successfully")
            
            if result.stdout:
                logging.info(f"Output: {result.stdout[:500]}...")
                self.response = f"I performed the '{check_name}' check and found:\n\n{result.stdout}"
                if "No autonomous system messages" in result.stdout or "All systems operating normally" in result.stdout:
                    self.response = "HEARTBEAT_OK"
            else:
                logging.info("No output from command")
                self.response = "HEARTBEAT_OK"
            
            # Update the check time
            self.update_check_time(check_name)
            
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running check {check_name}: {e}")
            logging.error(f"Error output: {e.stderr}")
            self.response = f"⚠️ Error during '{check_name}' check: {str(e)}\n\nPlease investigate this issue. Error details: {e.stderr}"
            return False
    
    def get_recommended_model(self, check_name: str) -> Dict[str, str]:
        """Get the recommended model and thinking level for a check"""
        if check_name not in CHECK_RUNNERS:
            return {"model": "haiku", "thinking": "low"}
        
        return {
            "model": CHECK_RUNNERS[check_name].get("model", "haiku"),
            "thinking": CHECK_RUNNERS[check_name].get("thinking", "low")
        }
    
    def run(self) -> Optional[str]:
        """
        Run the heartbeat system
        Returns the response message if any, or None
        """
        logging.info("Starting heartbeat run")
        
        # Determine which check to run
        check_name = self.determine_next_check()
        
        if not check_name:
            logging.info("No checks need to be run at this time.")
            return "HEARTBEAT_OK"
        
        # Run the check
        self.run_check(check_name)
        
        # Get the model recommendation
        model_rec = self.get_recommended_model(check_name)
        
        # Log the model recommendation
        logging.info(f"Recommended model for {check_name}: {model_rec['model']} with thinking level {model_rec['thinking']}")
        
        # Return the response
        if self.response and self.response != "HEARTBEAT_OK":
            # Add model recommendation for non-OK responses
            self.response += f"\n\n(This check would ideally use {model_rec['model']} model with {model_rec['thinking']} thinking level)"
        
        return self.response

def main() -> None:
    """Main function"""
    runner = HeartbeatRunner()
    response = runner.run()
    
    # Print the response for OpenClaw to see
    if response:
        print(response)
    else:
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()