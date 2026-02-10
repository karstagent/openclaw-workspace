#!/bin/bash
#
# Setup Script for Semantic Compression
# Installs dependencies and configures environment
#

# Set up error handling
set -e
trap 'echo "Error occurred at line $LINENO. Command: $BASH_COMMAND"' ERR

# Script variables
WORKSPACE="/Users/karst/.openclaw/workspace"
COMPRESSION_DIR="$WORKSPACE"

# Create log directory if it doesn't exist
mkdir -p "$WORKSPACE/logs"

# Function for logging
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$WORKSPACE/logs/compression_setup.log"
}

log "Starting semantic compression setup"

# Ensure we have Python 3
if ! command -v python3 &> /dev/null; then
  log "ERROR: Python 3 is not installed. Please install Python 3."
  exit 1
fi

# Create virtual environment
log "Creating Python virtual environment"
VENV_DIR="$WORKSPACE/venv_compression"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install dependencies
log "Installing dependencies"
pip install --upgrade pip
pip install torch transformers scikit-learn numpy tqdm sentence-transformers openai anthropic

# Verify installations
log "Verifying installations"
python -c "import torch; import transformers; import sklearn; import numpy; print('Core dependencies verified.')"

# Set up scripts
log "Setting up scripts"
chmod +x "$COMPRESSION_DIR/semantic_compression.py"
chmod +x "$COMPRESSION_DIR/api_integration.py"

# Create integration example script
cat > "$COMPRESSION_DIR/compression_example.py" << 'EOF'
#!/usr/bin/env python3
"""
Example usage of the semantic compression system
"""

import os
import sys
from api_integration import CompressionEnabledClient

# Example input
EXAMPLE_TEXT = """
[Paste a long document here for testing compression]
"""

def main():
    # Initialize the client with custom settings
    client = CompressionEnabledClient(
        compression_ratio=6,
        token_limit_threshold=100000,  # Set lower for testing
        verbose=True
    )
    
    # Create messages array
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": EXAMPLE_TEXT}
    ]
    
    # Process the messages
    compressed_messages, was_compressed = client._process_openai_messages(messages)
    
    # Print results
    print(f"Was compressed: {was_compressed}")
    print(f"Original length: {len(messages[1]['content'])}")
    print(f"Compressed length: {len(compressed_messages[1]['content'])}")
    
    if was_compressed:
        print("\nCompressed content preview:")
        print(compressed_messages[1]['content'][:500] + "...")

if __name__ == "__main__":
    main()
EOF

chmod +x "$COMPRESSION_DIR/compression_example.py"

# Create activation script
cat > "$COMPRESSION_DIR/activate_compression.sh" << EOF
#!/bin/bash
# Activate the compression environment
source "$VENV_DIR/bin/activate"
export PYTHONPATH="\$PYTHONPATH:$COMPRESSION_DIR"
echo "Semantic compression environment activated."
echo "Available commands:"
echo "  - semantic_compression.py: Compress documents directly"
echo "  - api_integration.py: Test API integration with compression"
echo "  - compression_example.py: Run a simple example"
EOF

chmod +x "$COMPRESSION_DIR/activate_compression.sh"

# Create README
cat > "$COMPRESSION_DIR/COMPRESSION_README.md" << 'EOF'
# Semantic Compression for LLMs

This system provides tools to compress text while preserving semantic meaning, allowing you to work with documents that exceed the token limits of large language models.

## Quick Start

1. Activate the environment:
   ```bash
   source ./activate_compression.sh
   ```

2. Compress a document:
   ```bash
   ./semantic_compression.py --input long_document.txt --output compressed.txt --ratio 6
   ```

3. Use the compression-enabled API client:
   ```python
   from api_integration import CompressionEnabledClient
   
   # For OpenAI
   client = CompressionEnabledClient()
   response = client.chat_completions_create(
       model="gpt-4",
       messages=[{"role": "user", "content": very_long_content}],
       max_tokens=4000
   )
   
   # For Anthropic
   client = CompressionEnabledClient()
   response = client.messages_create(
       model="claude-3-opus-20240229",
       messages=[{"role": "user", "content": very_long_content}],
       max_tokens=4000
   )
   ```

## Components

- `semantic_compression.py` - Core compression engine
- `api_integration.py` - API client with transparent compression
- `compression_example.py` - Example usage

## Options

### Compression Ratio

Control how aggressively text is compressed:
- Lower ratio (2-4): More detail preserved, less compression
- Medium ratio (5-8): Good balance of compression and detail
- Higher ratio (9+): Maximum compression, less detail

### Token Limit Threshold

Set the token count at which compression activates:
```python
client = CompressionEnabledClient(token_limit_threshold=150000)
```

### Compression Models

You can customize the models used for embedding and summarization:
```python
client = CompressionEnabledClient(
    embedding_model="sentence-transformers/all-mpnet-base-v2",
    summarizer_model="facebook/bart-large-cnn"
)
```

## Troubleshooting

If you encounter errors:

1. Ensure dependencies are installed:
   ```bash
   pip install torch transformers scikit-learn numpy tqdm sentence-transformers
   ```

2. Check CUDA compatibility if using GPU acceleration.

3. For large documents, try increasing compression ratio or processing in chunks.
EOF

log "Setting up environment variables"
echo "export PYTHONPATH=\"\$PYTHONPATH:$COMPRESSION_DIR\"" >> "$VENV_DIR/bin/activate"

log "Setup complete!"
log "To activate the environment, run: source $COMPRESSION_DIR/activate_compression.sh"
echo
echo "Setup complete! Run the following command to activate the compression environment:"
echo "source $COMPRESSION_DIR/activate_compression.sh"