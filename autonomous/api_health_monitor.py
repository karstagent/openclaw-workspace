#!/Users/karst/.openclaw/workspace/venv/bin/python
"""
API Health Monitor for OpenClaw
This script checks the health of various APIs used by the autonomous system.
"""

import os
import json
import datetime
import requests  # Now available from our virtual environment
import time
import logging
from typing import Dict, List, Any

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
LOGS_DIR = os.path.join(WORKSPACE, "logs")
STATUS_FILE = os.path.join(WORKSPACE, "autonomous_status.txt")
MESSAGES_DIR = os.path.join(WORKSPACE, "autonomous_messages")
HEALTH_LOG = os.path.join(LOGS_DIR, "api_health.log")

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(MESSAGES_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=HEALTH_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API endpoints to check
API_ENDPOINTS = {
    "OpenAI": {
        "url": "https://api.openai.com/v1/models",
        "headers": {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"
        },
        "critical": True
    },
    "Anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "headers": {
            "x-api-key": f"{os.environ.get('ANTHROPIC_API_KEY', '')}",
            "anthropic-version": "2024-03-01"
        },
        "critical": True
    },
    "OpenRouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "headers": {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"
        },
        "critical": True
    },
    "Vercel": {
        "url": "https://api.vercel.com/v1/projects",
        "headers": {
            "Authorization": f"Bearer {os.environ.get('VERCEL_API_KEY', '')}"
        },
        "critical": False
    }
}

class APIHealthMonitor:
    """
    Monitors the health of various API endpoints
    """
    def __init__(self):
        self.results = {}
        self.previous_results = self._load_previous_results()
        
    def _load_previous_results(self) -> Dict[str, Any]:
        """Load previous results from the API health log"""
        try:
            with open(os.path.join(WORKSPACE, "autonomous", "api_health.json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_results(self) -> None:
        """Save current results to the API health log"""
        try:
            with open(os.path.join(WORKSPACE, "autonomous", "api_health.json"), "w") as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save results: {str(e)}")
    
    def check_endpoints(self) -> Dict[str, Any]:
        """Check the health of all API endpoints"""
        for name, config in API_ENDPOINTS.items():
            logging.info(f"Checking {name} API...")
            try:
                response = requests.get(
                    config["url"],
                    headers=config["headers"],
                    timeout=10
                )
                
                status_code = response.status_code
                is_healthy = 200 <= status_code < 300
                
                self.results[name] = {
                    "healthy": is_healthy,
                    "statusCode": status_code,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "critical": config["critical"]
                }
                
                if is_healthy:
                    logging.info(f"{name} API is healthy (status code: {status_code})")
                else:
                    logging.warning(f"{name} API is unhealthy (status code: {status_code})")
            except Exception as e:
                logging.error(f"Error checking {name} API: {str(e)}")
                self.results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "critical": config["critical"]
                }
        
        return self.results
    
    def detect_changes(self) -> List[Dict[str, Any]]:
        """
        Detect changes in API health status
        Returns a list of APIs with changed health status
        """
        changes = []
        
        for name, current in self.results.items():
            # Skip if API wasn't checked before
            if name not in self.previous_results:
                continue
            
            previous = self.previous_results[name]
            
            # If health status has changed
            if current["healthy"] != previous["healthy"]:
                changes.append({
                    "name": name,
                    "critical": current["critical"],
                    "previous": previous["healthy"],
                    "current": current["healthy"],
                    "timestamp": current["timestamp"]
                })
        
        return changes
    
    def create_notification(self, changes: List[Dict[str, Any]]) -> str:
        """Create a notification message based on detected changes"""
        if not changes:
            return None
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        message_lines = [f"🚨 API Health Status Change ({timestamp})"]
        
        for change in changes:
            name = change["name"]
            status = "✅ Recovered" if change["current"] else "❌ Down"
            critical = " [CRITICAL]" if change["critical"] else ""
            
            message_lines.append(f"{status}: {name} API{critical}")
        
        # Add summary of all APIs
        message_lines.append("\nCurrent API Status:")
        
        for name, info in self.results.items():
            status = "✅ Healthy" if info["healthy"] else "❌ Unhealthy"
            critical = " [CRITICAL]" if info["critical"] else ""
            
            message_lines.append(f"• {name}{critical}: {status}")
        
        return "\n".join(message_lines)
    
    def send_notification(self, message: str) -> None:
        """Send a notification to the autonomous system"""
        try:
            # Create a unique message file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            message_file = os.path.join(MESSAGES_DIR, f"message_{timestamp}.txt")
            
            with open(message_file, "w") as f:
                f.write(message)
            
            logging.info(f"Notification sent: {message_file}")
        except Exception as e:
            logging.error(f"Failed to send notification: {str(e)}")
    
    def update_status_file(self) -> None:
        """Update the status file with API health information"""
        try:
            # Read existing content
            existing_content = ""
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f:
                    existing_content = f.read()
            
            # Create new API status section
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            api_status = [
                f"API Health Status - {timestamp}",
                "------------------------------"
            ]
            
            all_healthy = True
            for name, info in self.results.items():
                status = "✅ Healthy" if info["healthy"] else "❌ Unhealthy"
                if not info["healthy"]:
                    all_healthy = False
                api_status.append(f"{name}: {status}")
            
            api_status.append(f"Overall: {'✅ All APIs Healthy' if all_healthy else '❌ Some APIs Unhealthy'}")
            api_status.append("")
            
            # Append to existing content or create new
            with open(STATUS_FILE, "w") as f:
                f.write("\n".join(api_status))
                f.write("\n")
                f.write(existing_content)
        except Exception as e:
            logging.error(f"Failed to update status file: {str(e)}")
    
    def run(self) -> None:
        """Run the API health monitor"""
        logging.info("Starting API health monitoring...")
        
        try:
            # Check all endpoints
            self.check_endpoints()
            
            # Detect changes
            changes = self.detect_changes()
            
            # Create and send notification if needed
            if changes:
                message = self.create_notification(changes)
                if message:
                    self.send_notification(message)
            
            # Update status file
            self.update_status_file()
            
            # Save results
            self._save_results()
            
            logging.info("API health monitoring completed.")
        except Exception as e:
            logging.error(f"Error in API health monitoring: {str(e)}")

def main() -> None:
    """Main function"""
    monitor = APIHealthMonitor()
    monitor.run()

if __name__ == "__main__":
    main()