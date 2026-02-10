import json
import subprocess
import logging

logging.basicConfig(
    filename='/tmp/model_selection_minimal.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def update_config():
    try:
        with open('/Users/karst/.openclaw/openclaw.json', 'r') as f:
            config = json.load(f)
        
        # Explicitly add Opus model
        config['agents']['defaults']['models']['openrouter/anthropic/claude-3-opus'] = {
            'alias': 'opus'
        }
        
        with open('/Users/karst/.openclaw/openclaw.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info("Configuration updated successfully")
        return True
    except Exception as e:
        logging.error(f"Configuration update failed: {e}")
        return False

def main():
    update_config()
    logging.info("Model configuration update attempted")

if __name__ == "__main__":
    main()