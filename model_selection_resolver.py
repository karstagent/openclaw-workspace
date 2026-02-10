import json
import logging
import subprocess
import sys

# Logging configuration
logging.basicConfig(
    filename='/tmp/model_selection_debug.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def patch_openclaw_config():
    """Modify OpenClaw configuration to enable model selection"""
    try:
        # Read current configuration
        with open('/Users/karst/.openclaw/openclaw.json', 'r') as f:
            config = json.load(f)
        
        # Enhance model configuration
        config['agents']['defaults']['model_selection'] = {
            'enabled': True,
            'strategy': 'complexity_based',
            'complexity_map': {
                'openrouter/anthropic/claude-3-opus': ['high_complexity', 'strategic_tasks'],
                'openrouter/anthropic/claude-3.7-sonnet': ['medium_complexity'],
                'openrouter/anthropic/claude-3.5-haiku': ['low_complexity', 'routine_tasks'],
                'openrouter/deepseek/deepseek-coder': ['administrative_tasks']
            }
        }
        
        # Write updated configuration
        with open('/Users/karst/.openclaw/openclaw.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info("Configuration patched successfully")
        return True
    except Exception as e:
        logging.error(f"Configuration patch failed: {e}")
        return False

def restart_gateway():
    """Restart OpenClaw gateway to apply changes"""
    try:
        result = subprocess.run(['openclaw', 'gateway', 'restart'], 
                                capture_output=True, 
                                text=True, 
                                timeout=30)
        logging.info(f"Gateway restart output: {result.stdout}")
        logging.error(f"Gateway restart error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Gateway restart failed: {e}")
        return False

def main():
    logging.info("Starting Model Selection Resolution")
    
    # Patch configuration
    config_patched = patch_openclaw_config()
    
    # Restart gateway if configuration was patched
    if config_patched:
        gateway_restarted = restart_gateway()
        
        if gateway_restarted:
            logging.info("Model selection resolution completed successfully")
            sys.exit(0)
        else:
            logging.error("Gateway restart failed")
            sys.exit(1)
    else:
        logging.error("Configuration patch failed")
        sys.exit(1)

if __name__ == "__main__":
    main()