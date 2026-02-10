#!/bin/bash
# Install FAISS and sentence-transformers dependencies

set -e

echo "Installing FAISS and sentence-transformers dependencies..."

# Create a virtual environment if it doesn't exist
VENV_DIR="/Users/karst/.openclaw/workspace/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing faiss-cpu..."
pip install --upgrade pip
pip install faiss-cpu

echo "Installing sentence-transformers..."
pip install sentence-transformers

# Create an empty __init__.py file to make the workspace a proper package
touch /Users/karst/.openclaw/workspace/__init__.py

echo "Dependencies installed successfully."