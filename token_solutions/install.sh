#!/bin/bash

# Install Token Solutions to a new environment
# Usage: ./install.sh [target_dir]

set -e

# Default target directory
TARGET_DIR="${1:-$HOME/.token_solutions}"

# Create directories
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/logs"
mkdir -p "$TARGET_DIR/config"

# Copy files to target directory
cp *.py "$TARGET_DIR/"
cp README.md "$TARGET_DIR/"

if [ -f "../config/token_solutions.json" ]; then
    cp ../config/token_solutions.json "$TARGET_DIR/config/"
else
    # Create default config
    cat > "$TARGET_DIR/config/token_solutions.json" << 'EOCFG'
{
  "semantic_compression": {
    "enabled": true,
    "default_compression_ratio": 6,
    "token_threshold": 150000,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "summarizer_model": "facebook/bart-large-cnn",
    "preserve_structure": true
  },
  "context_extension": {
    "enabled": true,
    "target_context_length": 400000,
    "fallback_to_compression": true,
    "api_type": "openai"
  },
  "monitoring": {
    "log_level": "info",
    "track_token_savings": true,
    "save_statistics": true,
    "statistics_file": "token_usage_stats.jsonl"
  }
}
EOCFG
fi

# Create virtual environment
python3 -m venv "$TARGET_DIR/venv"
source "$TARGET_DIR/venv/bin/activate"

# Install dependencies
pip install --upgrade pip
pip install torch transformers scikit-learn numpy tqdm sentence-transformers openai anthropic

# Make scripts executable
chmod +x "$TARGET_DIR"/*.py

# Create activation script
cat > "$TARGET_DIR/activate.sh" << EOA
#!/bin/bash
# Activate the token solutions environment
source "$TARGET_DIR/venv/bin/activate"
export PYTHONPATH="\$PYTHONPATH:$TARGET_DIR"
echo "Token solutions environment activated."
EOA

chmod +x "$TARGET_DIR/activate.sh"

echo "Installation complete!"
echo "To activate the environment, run: source $TARGET_DIR/activate.sh"
