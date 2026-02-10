import json
import logging
import sys

logging.basicConfig(
    filename='/tmp/model_selection_diagnostic.log', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def load_openclaw_config():
    """Load OpenClaw configuration"""
    try:
        with open('/Users/karst/.openclaw/openclaw.json', 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return None

def analyze_model_configuration(config):
    """Analyze model configuration details"""
    if not config:
        logging.error("No configuration found")
        return

    models = config['agents']['defaults']['models']
    primary_model = config['agents']['defaults']['model']['primary']

    logging.info("Model Configuration Analysis:")
    logging.info(f"Primary Model: {primary_model}")
    logging.info("Available Models:")
    for model_key, model_details in models.items():
        logging.info(f"- {model_key}: {model_details}")

def main():
    config = load_openclaw_config()
    if config:
        analyze_model_configuration(config)
    else:
        logging.error("Configuration analysis failed")

if __name__ == "__main__":
    main()