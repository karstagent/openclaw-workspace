import json
import subprocess
import logging

logging.basicConfig(
    filename='/tmp/model_selection_patch.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def update_config():
    try:
        with open('/Users/karst/.openclaw/openclaw.json', 'r') as f:
            config = json.load(f)
        
        # Modify existing models configuration
        config['agents']['defaults']['models']['openrouter/anthropic/claude-3-opus'] = {
            'alias': 'opus',
            'priority': 'high_complexity'
        }
        
        with open('/Users/karst/.openclaw/openclaw.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info("Configuration updated successfully")
        return True
    except Exception as e:
        logging.error(f"Configuration update failed: {e}")
        return False

def restart_gateway():
    try:
        result = subprocess.run(['openclaw', 'gateway', 'restart'], 
                                capture_output=True, 
                                text=True)
        logging.info(f"Gateway restart output: {result.stdout}")
        logging.error(f"Gateway restart error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Gateway restart failed: {e}")
        return False

def main():
    if update_config():
        restart_gateway()
        logging.info("Model configuration update complete")

if __name__ == "__main__":
    main()