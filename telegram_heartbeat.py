import os
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/tmp/telegram_heartbeat.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TelegramHeartbeat:
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
            
            logging.info(f"Attempting to send message to Telegram")
            response = requests.post(url, json=payload, timeout=10)
            
            logging.info(f"Telegram API Response Status: {response.status_code}")
            logging.info(f"Telegram API Response Content: {response.text}")
            
            return response.status_code == 200
        
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False

def main():
    heartbeat = TelegramHeartbeat()
    success = heartbeat.send_telegram_message()
    logging.info(f"Heartbeat message send result: {success}")

if __name__ == "__main__":
    main()