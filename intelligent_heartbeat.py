import os
import json
import schedule
import time
from datetime import datetime

class IntelligentHeartbeat:
    def __init__(self):
        self.state_file = '/Users/karst/.openclaw/workspace/heartbeat_state.json'
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

    def update_research_context(self, updates):
        """Dynamically update research context"""
        self.research_context.update(updates)
        self._save_state()

    def _save_state(self):
        """Save current research state to persistent storage"""
        with open(self.state_file, 'w') as f:
            json.dump(self.research_context, f, indent=2)

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

    def send_heartbeat(self):
        """Send heartbeat using OpenClaw messaging"""
        try:
            import subprocess
            message = self.generate_heartbeat_message()
            
            result = subprocess.run([
                'openclaw', 'message', 'send', 
                '--target', '535786496', 
                '--message', message
            ], capture_output=True, text=True)
            
            print(f"Heartbeat sent. Result: {result.stdout}")
        except Exception as e:
            print(f"Heartbeat sending failed: {e}")

def main():
    heartbeat = IntelligentHeartbeat()
    schedule.every(5).minutes.do(heartbeat.send_heartbeat)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()