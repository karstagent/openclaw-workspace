import os
import json
import logging
import requests
import schedule
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/tmp/periodic_heartbeat.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PeriodicHeartbeat:
    TELEGRAM_BOT_TOKEN = "8321959949:AAFe7LZrQLe5XaqWfHWoRjrNlZL7PW5vmPA"
    CHAT_ID = "535786496"

    def __init__(self):
        self.research_context = {
            'primary_focus': 'Cryptocurrency Bot Development',
            'active_streams': [
                'QMD Skill Integration',
                'Local Embedding Strategy',
                'Crypto Bot Architecture Design'
            ],
            'metacognitive_stage': 'User-Centric Product Design',
            'key_objectives': [
                'Design MVP for Crypto Bot Platform',
                'Simplify Blockchain Interaction Model',
                'Develop Adaptive Agent Architecture'
            ]
        }

    def generate_heartbeat_message(self):
        """Create a comprehensive, context-rich update"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""🧠 Autonomous Research Update

🔬 Focus: {self.research_context['primary_focus']}
🕰️ Timestamp: {timestamp}

🚀 Active Research Streams:
{chr(10).join(f'• {stream}' for stream in self.research_context['active_streams'])}

🎯 Key Objectives:
{chr(10).join(f'• {obj}' for obj in self.research_context['key_objectives'])}

🔍 Metacognitive Stage: 
{self.research_context['metacognitive_stage']}

💡 Continuous autonomous optimization in progress."""
        
        return message

    def send_telegram_message(self):
        """Send message directly via Telegram API with comprehensive logging"""
        message = self.generate_heartbeat_message()
        
        try:
            url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.CHAT_ID,
                "text": message
            }
            
            logging.info(f"Attempting to send periodic heartbeat message")
            response = requests.post(url, json=payload, timeout=10)
            
            logging.info(f"Telegram API Response Status: {response.status_code}")
            logging.info(f"Telegram API Response Content: {response.text}")
            
            return response.status_code == 200
        
        except Exception as e:
            logging.error(f"Error sending periodic Telegram message: {e}")
            return False

def main():
    heartbeat = PeriodicHeartbeat()
    
    # Schedule the heartbeat every 5 minutes
    schedule.every(5).minutes.do(heartbeat.send_telegram_message)
    
    logging.info("Periodic Heartbeat System Started")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()