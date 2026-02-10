import schedule
import time
import logging
from datetime import datetime
import os

# Logging configuration
logging.basicConfig(
    filename='/tmp/unified_heartbeat.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global state tracking
GLOBAL_STATE = {
    'current_context': {
        'primary_focus': 'Cryptocurrency Bot Product Development',
        'research_stage': 'User-Centric Design',
        'key_objectives': [
            'Define Minimum Viable Product (MVP) features',
            'Design intuitive user interface',
            'Simplify blockchain interaction mechanisms'
        ]
    },
    'last_message_hash': None
}

def generate_heartbeat_message():
    """Generate a single, comprehensive heartbeat message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""🚀 {GLOBAL_STATE['current_context']['primary_focus']}

🕰️ Timestamp: {timestamp}

🔍 Research Stage: {GLOBAL_STATE['current_context']['research_stage']}

🎯 Key Objectives:
{chr(10).join('• ' + obj for obj in GLOBAL_STATE['current_context']['key_objectives'])}

💻 System Status:
• Timestamp: {timestamp}
• Active: Continuous optimization"""

    return message

def send_message(message):
    """Send message using OpenClaw's native messaging system"""
    try:
        import subprocess
        result = subprocess.run([
            'openclaw', 'message', 'send', 
            '--target', '535786496', 
            '--message', message
        ], capture_output=True, text=True)
        
        logging.info(f"Message send result: {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Message send error: {e}")
        return False

def heartbeat():
    """Primary heartbeat method with single message send"""
    try:
        message = generate_heartbeat_message()
        send_message(message)
    except Exception as e:
        logging.error(f"Heartbeat failed: {e}")

# Schedule heartbeat
schedule.every(5).minutes.do(heartbeat)

# Logging startup
logging.info("Unified Heartbeat System Initialized")

# Keep script running
while True:
    schedule.run_pending()
    time.sleep(1)
