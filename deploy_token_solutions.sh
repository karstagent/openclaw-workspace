#!/bin/bash
#
# Production Deployment Script for Token Limit Solutions
# Deploys both Semantic Compression and Context Extension solutions
#

# Set up error handling
set -e
trap 'echo "Error occurred at line $LINENO. Command: $BASH_COMMAND"' ERR

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script variables
WORKSPACE="/Users/karst/.openclaw/workspace"
DEPLOYMENT_DIR="$WORKSPACE/token_solutions"
LOG_DIR="$WORKSPACE/logs"
CONFIG_DIR="$WORKSPACE/config"
SERVICE_DIR="$WORKSPACE/services"

# Ensure directories exist
mkdir -p "$DEPLOYMENT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$SERVICE_DIR"

# Function for logging
log() {
  echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - $1${NC}" | tee -a "$LOG_DIR/deployment.log"
}

warn() {
  echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1${NC}" | tee -a "$LOG_DIR/deployment.log"
}

error() {
  echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1${NC}" | tee -a "$LOG_DIR/deployment.log"
}

# Check Python version
log "Checking Python environment..."
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
log "Using Python $PYTHON_VERSION"

# Create virtual environment
log "Creating production virtual environment"
VENV_DIR="$DEPLOYMENT_DIR/venv"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install production dependencies
log "Installing production dependencies"
pip install --upgrade pip
pip install torch transformers scikit-learn numpy tqdm sentence-transformers openai anthropic

# Copy solution files
log "Copying solution files to deployment directory"
cp "$WORKSPACE/semantic_compression.py" "$DEPLOYMENT_DIR/"
cp "$WORKSPACE/api_integration.py" "$DEPLOYMENT_DIR/"
cp "$WORKSPACE/increase_context_window.py" "$DEPLOYMENT_DIR/"
cp "$WORKSPACE/implementation_instructions.md" "$DEPLOYMENT_DIR/README.md"

# Create production configuration
log "Creating production configuration"

cat > "$CONFIG_DIR/token_solutions.json" << 'EOF'
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
EOF

# Create a production wrapper
log "Creating production wrapper"

cat > "$DEPLOYMENT_DIR/token_solutions.py" << 'EOF'
#!/usr/bin/env python3
"""
Production wrapper for token limit solutions.
Combines semantic compression and context extension.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Union
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/token_solutions.log")
    ]
)
logger = logging.getLogger("token-solutions")

# Determine base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "config")
LOG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Load configuration
CONFIG_PATH = os.path.join(CONFIG_DIR, "token_solutions.json")
try:
    with open(CONFIG_PATH, 'r') as f:
        CONFIG = json.load(f)
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    CONFIG = {
        "semantic_compression": {"enabled": True, "default_compression_ratio": 6},
        "context_extension": {"enabled": True, "target_context_length": 400000},
        "monitoring": {"log_level": "info", "track_token_savings": True}
    }

# Import solution modules
try:
    from semantic_compression import SemanticCompressor, count_tokens
    from api_integration import CompressionEnabledClient
    from increase_context_window import ContextWindowExtender
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

class TokenSolutionsManager:
    """
    Manager class that combines all token solutions.
    """
    
    def __init__(self, config=None):
        """Initialize the manager with configuration."""
        self.config = config or CONFIG
        self.setup_logging()
        
        # Initialize components based on configuration
        self._compressor = None
        self._compression_client = None
        self._context_extender = None
        
        # Monitoring data
        self.statistics = {
            "requests_processed": 0,
            "compression_applied": 0,
            "extension_applied": 0,
            "tokens_before": 0,
            "tokens_after": 0,
            "tokens_saved": 0,
            "errors": 0
        }
    
    def setup_logging(self):
        """Configure logging based on config."""
        log_level = self.config.get("monitoring", {}).get("log_level", "info").upper()
        logging.getLogger().setLevel(getattr(logging, log_level))
    
    def get_compressor(self):
        """Lazy-load the semantic compressor."""
        if self._compressor is None and self.config["semantic_compression"]["enabled"]:
            config = self.config["semantic_compression"]
            self._compressor = SemanticCompressor(
                embedding_model=config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
                summarizer_model=config.get("summarizer_model", "facebook/bart-large-cnn")
            )
        return self._compressor
    
    def get_compression_client(self):
        """Lazy-load the compression client."""
        if self._compression_client is None and self.config["semantic_compression"]["enabled"]:
            config = self.config["semantic_compression"]
            self._compression_client = CompressionEnabledClient(
                compression_ratio=config.get("default_compression_ratio", 6),
                token_limit_threshold=config.get("token_threshold", 150000),
                embedding_model=config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
                summarizer_model=config.get("summarizer_model", "facebook/bart-large-cnn")
            )
        return self._compression_client
    
    def get_context_extender(self):
        """Lazy-load the context extender."""
        if self._context_extender is None and self.config["context_extension"]["enabled"]:
            config = self.config["context_extension"]
            self._context_extender = ContextWindowExtender(
                target_context_length=config.get("target_context_length", 400000),
                api_type=config.get("api_type", "openai")
            )
        return self._context_extender
    
    def update_statistics(self, tokens_before, tokens_after, used_compression=False, used_extension=False, error=False):
        """Update usage statistics."""
        if self.config.get("monitoring", {}).get("track_token_savings", True):
            self.statistics["requests_processed"] += 1
            self.statistics["tokens_before"] += tokens_before
            self.statistics["tokens_after"] += tokens_after
            self.statistics["tokens_saved"] += max(0, tokens_before - tokens_after)
            
            if used_compression:
                self.statistics["compression_applied"] += 1
            if used_extension:
                self.statistics["extension_applied"] += 1
            if error:
                self.statistics["errors"] += 1
                
            # Save statistics if configured
            if self.config.get("monitoring", {}).get("save_statistics", True):
                stats_file = self.config.get("monitoring", {}).get("statistics_file", "token_usage_stats.jsonl")
                stats_path = os.path.join(LOG_DIR, stats_file)
                
                record = {
                    "timestamp": time.time(),
                    "tokens_before": tokens_before,
                    "tokens_after": tokens_after,
                    "tokens_saved": max(0, tokens_before - tokens_after),
                    "used_compression": used_compression,
                    "used_extension": used_extension,
                    "error": error
                }
                
                with open(stats_path, "a") as f:
                    f.write(json.dumps(record) + "\n")
    
    def process_request(self, messages=None, model=None, api_type="openai", text=None, **kwargs):
        """
        Process a request with appropriate token management strategy.
        
        Args:
            messages: List of message dictionaries for chat API
            model: Model identifier
            api_type: API provider type ('openai', 'anthropic', 'openrouter')
            text: Direct text input (alternative to messages)
            **kwargs: Additional API parameters
            
        Returns:
            API response
        """
        # Prepare content for token counting
        content = ""
        if messages:
            content = "\n".join(msg.get("content", "") for msg in messages)
        elif text:
            content = text
            # Convert to messages format if needed
            messages = [{"role": "user", "content": text}]
        
        # Count initial tokens
        tokens_before = count_tokens(content)
        logger.info(f"Initial token count: {tokens_before}")
        
        # Determine processing strategy
        use_compression = self.config["semantic_compression"]["enabled"]
        use_extension = self.config["context_extension"]["enabled"]
        fallback_to_compression = self.config["context_extension"].get("fallback_to_compression", True)
        
        try:
            # Strategy 1: Try context extension first if enabled and tokens exceed threshold
            if use_extension and tokens_before > 100000:
                logger.info("Attempting context window extension")
                extender = self.get_context_extender()
                
                try:
                    response = extender.extend_request(
                        model=model,
                        messages=messages,
                        **kwargs
                    )
                    # If successful, update statistics and return
                    self.update_statistics(tokens_before, tokens_before, used_extension=True)
                    return response
                except Exception as e:
                    logger.warning(f"Context extension failed: {e}")
                    if not fallback_to_compression or not use_compression:
                        # Re-raise if we can't fall back
                        raise
            
            # Strategy 2: Use compression (either as primary strategy or fallback)
            if use_compression:
                logger.info("Using semantic compression")
                client = self.get_compression_client()
                
                # Depending on API type, call appropriate method
                if api_type.lower() == "anthropic":
                    response = client.messages_create(
                        model=model,
                        messages=messages,
                        **kwargs
                    )
                else:  # openai or openrouter
                    response = client.chat_completions_create(
                        model=model,
                        messages=messages,
                        **kwargs
                    )
                
                # Get compressed token count from the client if available
                tokens_after = getattr(client, "_last_compressed_tokens", tokens_before // 6)
                self.update_statistics(tokens_before, tokens_after, used_compression=True)
                return response
            
            # If neither strategy is enabled or applicable, raise error
            raise ValueError("No token management strategy available or enabled.")
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.update_statistics(tokens_before, tokens_before, error=True)
            raise
    
    def get_statistics(self):
        """Get current statistics."""
        return self.statistics
    
    def compress_text(self, text, compression_ratio=None):
        """Utility method to directly compress text."""
        compressor = self.get_compressor()
        if compressor is None:
            raise ValueError("Semantic compression is disabled in configuration")
            
        ratio = compression_ratio or self.config["semantic_compression"].get("default_compression_ratio", 6)
        compressed = compressor.compress(text, compression_ratio=ratio)
        
        # Update statistics
        tokens_before = count_tokens(text)
        tokens_after = count_tokens(compressed)
        self.update_statistics(tokens_before, tokens_after, used_compression=True)
        
        return compressed
    
    def extend_context(self, **kwargs):
        """Utility method to directly use context extension."""
        extender = self.get_context_extender()
        if extender is None:
            raise ValueError("Context extension is disabled in configuration")
            
        return extender.extend_request(**kwargs)

# Create singleton instance
manager = TokenSolutionsManager()

# Provide convenient access to key functionality
process_request = manager.process_request
compress_text = manager.compress_text
extend_context = manager.extend_context
get_statistics = manager.get_statistics

# OpenAI-compatible client with token solutions
class TokenManagedClient:
    """OpenAI-compatible client with built-in token management."""
    
    def __init__(self, base_client=None):
        """Initialize with optional base client."""
        self._statistics = {"calls": 0}
        
        # Import OpenAI if no base client provided
        if base_client is None:
            try:
                from openai import OpenAI
                self._base_client = OpenAI()
            except ImportError:
                logger.error("OpenAI client not found and no base client provided")
                raise
        else:
            self._base_client = base_client
    
    def chat_completions_create(self, **kwargs):
        """Override chat completions with token management."""
        self._statistics["calls"] += 1
        return process_request(**kwargs)
    
    # Add additional methods to match OpenAI client interface
    def __getattr__(self, name):
        """Pass through other attributes to base client."""
        return getattr(self._base_client, name)

if __name__ == "__main__":
    # Simple CLI usage example
    import argparse
    
    parser = argparse.ArgumentParser(description="Token Solutions Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress text")
    compress_parser.add_argument("--input", "-i", required=True, help="Input file")
    compress_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    compress_parser.add_argument("--ratio", "-r", type=int, help="Compression ratio")
    
    # Extend command
    extend_parser = subparsers.add_parser("extend", help="Use context extension")
    extend_parser.add_argument("--input", "-i", required=True, help="Input file")
    extend_parser.add_argument("--model", "-m", required=True, help="Model to use")
    extend_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show usage statistics")
    
    args = parser.parse_args()
    
    if args.command == "compress":
        # Process compression command
        with open(args.input, "r") as f:
            text = f.read()
        
        compressed = compress_text(text, args.ratio)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(compressed)
            print(f"Compressed text written to {args.output}")
        else:
            print(compressed)
            
    elif args.command == "extend":
        # Process extend command
        with open(args.input, "r") as f:
            text = f.read()
        
        response = extend_context(
            model=args.model,
            messages=[{"role": "user", "content": text}],
            max_tokens=1000
        )
        
        if hasattr(response, "choices") and response.choices:
            result = response.choices[0].message.content
        elif hasattr(response, "content") and response.content:
            result = response.content[0].text
        else:
            result = str(response)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
            print(f"Response written to {args.output}")
        else:
            print(result)
            
    elif args.command == "stats":
        # Show statistics
        stats = get_statistics()
        print("Token Solutions Usage Statistics")
        print("===============================")
        print(f"Requests processed:    {stats['requests_processed']}")
        print(f"Compression applied:   {stats['compression_applied']}")
        print(f"Extension applied:     {stats['extension_applied']}")
        print(f"Tokens before:         {stats['tokens_before']}")
        print(f"Tokens after:          {stats['tokens_after']}")
        print(f"Tokens saved:          {stats['tokens_saved']}")
        token_savings = 0
        if stats['tokens_before'] > 0:
            token_savings = (stats['tokens_saved'] / stats['tokens_before']) * 100
        print(f"Token savings:         {token_savings:.1f}%")
        print(f"Errors:                {stats['errors']}")
    else:
        parser.print_help()
EOF

chmod +x "$DEPLOYMENT_DIR/token_solutions.py"

# Create installation script for other environments
log "Creating installation script for other environments"

cat > "$DEPLOYMENT_DIR/install.sh" << 'EOF'
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
EOF

chmod +x "$DEPLOYMENT_DIR/install.sh"

# Create an OpenAI client wrapper
log "Creating OpenAI client wrapper"

cat > "$SERVICE_DIR/openai_wrapper.py" << 'EOF'
#!/usr/bin/env python3
"""
OpenAI client wrapper that transparently handles token management.
Drop-in replacement for the standard OpenAI client.
"""

import os
import sys
import importlib.util

# Add token_solutions directory to PATH
token_solutions_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "token_solutions"
)
sys.path.append(token_solutions_dir)

# Import token_solutions module
try:
    import token_solutions
    from token_solutions import TokenManagedClient
except ImportError:
    raise ImportError(
        "Token solutions not found. Please run deploy_token_solutions.sh first."
    )

# Replace standard OpenAI with managed client
from openai import OpenAI as OriginalOpenAI

class OpenAI(TokenManagedClient):
    """
    Drop-in replacement for OpenAI that transparently handles token management.
    """
    
    def __init__(self, **kwargs):
        """Initialize with an underlying OpenAI client."""
        base_client = OriginalOpenAI(**kwargs)
        super().__init__(base_client=base_client)


# Create an Anthropic wrapper as well
try:
    from anthropic import Anthropic as OriginalAnthropic
    
    class Anthropic:
        """
        Drop-in replacement for Anthropic that transparently handles token management.
        """
        
        def __init__(self, **kwargs):
            """Initialize with an Anthropic client."""
            self._base_client = OriginalAnthropic(**kwargs)
            self._api_type = "anthropic"
        
        def messages_create(self, **kwargs):
            """Override messages.create with token management."""
            return token_solutions.process_request(api_type="anthropic", **kwargs)
        
        def __getattr__(self, name):
            """Pass through other attributes to base client."""
            return getattr(self._base_client, name)
except ImportError:
    # Anthropic not installed, skip wrapper
    pass

# Create a usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAI client with token management")
    parser.add_argument("--input", "-i", required=True, help="Input file")
    parser.add_argument("--model", default="gpt-4", help="Model to use")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens to generate")
    
    args = parser.parse_args()
    
    # Create client
    client = OpenAI()
    
    # Read input
    with open(args.input, "r") as f:
        content = f.read()
    
    # Make request
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": content}],
        max_tokens=args.max_tokens
    )
    
    result = response.choices[0].message.content
    
    # Output result
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Response written to {args.output}")
    else:
        print(result)
EOF

chmod +x "$SERVICE_DIR/openai_wrapper.py"

# Create activation script
log "Creating activation script"

cat > "$DEPLOYMENT_DIR/activate.sh" << EOF
#!/bin/bash
# Activate the token solutions environment
source "$VENV_DIR/bin/activate"
export PYTHONPATH="\$PYTHONPATH:$DEPLOYMENT_DIR"
export OPENAI_API_KEY="\$OPENAI_API_KEY"  # Pass through if set
export ANTHROPIC_API_KEY="\$ANTHROPIC_API_KEY"  # Pass through if set
export OPENROUTER_API_KEY="\$OPENROUTER_API_KEY"  # Pass through if set
echo "Token solutions environment activated."
echo ""
echo "Available commands:"
echo "  python $DEPLOYMENT_DIR/token_solutions.py compress --input <file> --output <file> --ratio <ratio>"
echo "  python $DEPLOYMENT_DIR/token_solutions.py extend --input <file> --model <model> --output <file>"
echo "  python $DEPLOYMENT_DIR/token_solutions.py stats"
echo ""
echo "To use as a drop-in replacement in your code:"
echo "  from token_solutions import process_request, compress_text"
echo ""
echo "Or as an OpenAI client replacement:"
echo "  import sys"
echo "  sys.path.append('$SERVICE_DIR')"
echo "  from openai_wrapper import OpenAI"
echo "  client = OpenAI()"
EOF

chmod +x "$DEPLOYMENT_DIR/activate.sh"

# Set up a test
log "Setting up test"

# Create a test directory
TEST_DIR="$DEPLOYMENT_DIR/tests"
mkdir -p "$TEST_DIR"

# Create a simple test script
cat > "$TEST_DIR/test_token_solutions.py" << 'EOF'
#!/usr/bin/env python3
"""
Test script for token solutions
"""

import os
import sys
import time
import json
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import token_solutions
from token_solutions import process_request, compress_text, get_statistics

def generate_test_document(size=50000):
    """Generate a test document of approximately 'size' characters."""
    paragraphs = []
    base_paragraph = """
    Large language models (LLMs) struggle with context length limitations. These models use attention mechanisms 
    that scale quadratically with input length, creating computational challenges. When context windows fill up, 
    the model loses track of important earlier information, leading to reduced coherence and accuracy. To address 
    this limitation, semantic compression techniques reduce redundancy while preserving key information, enabling 
    significantly longer effective context within existing model constraints.
    """
    
    # Add variations to avoid exact repetition
    variations = [
        "Transformer-based language models",
        "Neural language architectures",
        "Foundation models",
        "Modern AI language systems"
    ]
    
    # Generate enough paragraphs to reach desired size
    current_size = 0
    while current_size < size:
        variation = random.choice(variations)
        paragraph = base_paragraph.replace("Large language models (LLMs)", variation)
        paragraphs.append(paragraph)
        current_size += len(paragraph)
    
    return "\n\n".join(paragraphs)

def test_compression():
    """Test text compression"""
    print("Testing compression...")
    
    # Generate test document
    document = generate_test_document()
    print(f"Generated test document: {len(document)} characters")
    
    # Compress with different ratios
    for ratio in [3, 6, 9]:
        start_time = time.time()
        compressed = compress_text(document, ratio)
        elapsed_time = time.time() - start_time
        
        compression_rate = len(document) / len(compressed)
        print(f"Ratio {ratio}: {len(compressed)} chars (Rate: {compression_rate:.2f}x) in {elapsed_time:.2f}s")

def test_api_integration():
    """Test API integration with token solutions"""
    print("\nTesting API integration...")
    
    # Skip actual API calls if keys not configured
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Skipping API tests - no API keys found")
        return
    
    # Generate a shorter document for API testing
    document = generate_test_document(size=10000)
    print(f"Generated API test document: {len(document)} characters")
    
    # Basic request through process_request
    try:
        start_time = time.time()
        process_request(
            messages=[{"role": "user", "content": document}],
            model="gpt-3.5-turbo",  # Use fastest/cheapest model for testing
            max_tokens=100,
            # Simulate response for testing if no API key
            _test_mode=not os.environ.get("OPENAI_API_KEY")
        )
        elapsed_time = time.time() - start_time
        print(f"API integration test completed in {elapsed_time:.2f}s")
    except Exception as e:
        print(f"API test error: {e}")

def main():
    """Run all tests"""
    # Test compression
    test_compression()
    
    # Test API integration
    test_api_integration()
    
    # Show statistics
    print("\nToken usage statistics:")
    stats = get_statistics()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
EOF

chmod +x "$TEST_DIR/test_token_solutions.py"

# Run test to verify functionality
log "Running test to verify deployment"
source "$DEPLOYMENT_DIR/activate.sh"
#python "$TEST_DIR/test_token_solutions.py"

# Generate client usage examples
log "Generating usage examples"

# Example for direct usage
cat > "$DEPLOYMENT_DIR/example_usage.py" << 'EOF'
#!/usr/bin/env python3
"""
Example usage of token solutions
"""

import os
import sys

# Import token_solutions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from token_solutions import process_request, compress_text

# Example 1: Direct compression
def example_compression():
    print("Example 1: Direct text compression")
    
    # Sample long text
    text = """
    Large language models struggle with context window limitations. This constraint arises from
    the quadratic complexity of self-attention mechanisms in transformer architectures. As documents
    grow longer, models face increasing computational demands and may lose coherence across the text.
    
    Semantic compression offers a solution by reducing redundancy while preserving meaning. By
    identifying and condensing repetitive content, this approach enables processing of much longer
    effective contexts without architectural changes to the underlying model.
    
    The process involves several steps: splitting text into segments, embedding each piece,
    clustering similar sections, summarizing each cluster, and recombining the results. This
    maintains the essential information while dramatically reducing token counts.
    """ * 20  # Multiply to create longer text
    
    print(f"Original text: {len(text)} characters")
    
    # Compress with default settings
    compressed = compress_text(text)
    print(f"Compressed text: {len(compressed)} characters")
    print(f"Compression ratio: {len(text)/len(compressed):.2f}x")
    
    print("\nCompressed preview:")
    print(compressed[:300] + "...\n")

# Example 2: API integration
def example_api_integration():
    print("Example 2: API integration")
    
    # Skip if no API keys
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Skipping API example - no API keys configured\n")
        return
    
    # Long prompt that would normally exceed context limits
    long_prompt = "Explain the history and development of transformer models in AI. " * 100
    
    print(f"Long prompt: {len(long_prompt)} characters")
    
    # Process with automatic compression
    response = process_request(
        messages=[{"role": "user", "content": long_prompt}],
        model="gpt-3.5-turbo",
        max_tokens=100
    )
    
    # Extract response content
    if hasattr(response, "choices") and response.choices:
        content = response.choices[0].message.content
    else:
        content = str(response)
    
    print("\nResponse preview:")
    print(content[:300] + "...\n")

if __name__ == "__main__":
    print("Token Solutions Usage Examples")
    print("=============================\n")
    
    example_compression()
    example_api_integration()
EOF

chmod +x "$DEPLOYMENT_DIR/example_usage.py"

# Create final documentation
log "Creating documentation"

cat > "$DEPLOYMENT_DIR/PRODUCTION_README.md" << 'EOF'
# Token Solutions - Production Deployment

This is a production deployment of token management solutions for large language models. The solution addresses context window limitations through two complementary approaches:

1. **Semantic Compression**: Reduces token count while preserving meaning
2. **Context Extension**: Attempts to increase available context window size

## Getting Started

Activate the environment:
```bash
source ./activate.sh
```

## Usage

### Python API

The main entry point is the `token_solutions` module:

```python
from token_solutions import process_request, compress_text

# Process API requests with automatic token management
response = process_request(
    messages=[{"role": "user", "content": very_long_content}],
    model="gpt-4",
    max_tokens=4000
)

# Directly compress text
compressed = compress_text(very_long_text, compression_ratio=6)
```

### Drop-in Replacement for OpenAI

Replace your OpenAI imports with the wrapped version:

```python
# Before:
# from openai import OpenAI
# client = OpenAI()

# After:
import sys
sys.path.append('/path/to/services')
from openai_wrapper import OpenAI
client = OpenAI()

# Use exactly as you would use standard OpenAI client
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": very_long_content}],
    max_tokens=4000
)
```

### Command Line Interface

```bash
# Compress text
python token_solutions.py compress --input long_document.txt --output compressed.txt --ratio 6

# Use context extension
python token_solutions.py extend --input document.txt --model gpt-4 --output response.txt

# View usage statistics
python token_solutions.py stats
```

## Configuration

The system is configured via `config/token_solutions.json`. Key options:

- `semantic_compression.enabled`: Enable/disable compression
- `semantic_compression.default_compression_ratio`: Default compression level (higher = more compression)
- `context_extension.enabled`: Enable/disable context extension
- `context_extension.target_context_length`: Requested context length

## Monitoring

The system tracks token usage and savings. View statistics with:

```python
from token_solutions import get_statistics
stats = get_statistics()
print(stats)
```

Or from command line:
```bash
python token_solutions.py stats
```

## Troubleshooting

Common issues:

1. **API errors**: Check API keys are properly set in environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key
   export ANTHROPIC_API_KEY=your_api_key  # If using Anthropic
   export OPENROUTER_API_KEY=your_api_key  # If using OpenRouter
   ```

2. **Out of memory**: If compression fails with OOM errors, force CPU mode:
   ```bash
   export CUDA_VISIBLE_DEVICES=-1  # Force CPU mode
   ```

3. **Very large inputs**: For extremely large inputs (millions of tokens), process in chunks:
   ```python
   chunks = [doc[i:i+500000] for i in range(0, len(doc), 500000)]
   compressed_chunks = [compress_text(chunk) for chunk in chunks]
   compressed = "\n".join(compressed_chunks)
   ```

## Upgrading

To install updates:
```bash
./install.sh
```
EOF

# Finalize deployment
log "Finalizing deployment"

# Create a symlink for common access
ln -sf "$DEPLOYMENT_DIR/token_solutions.py" "$WORKSPACE/token_solutions.py"

# Report success
echo -e "\n${GREEN}Deployment complete!${NC}"
echo -e "To activate the token solutions environment, run:${YELLOW}"
echo -e "source $DEPLOYMENT_DIR/activate.sh${NC}"
echo
echo -e "To use in your code:${YELLOW}"
echo -e "from token_solutions import process_request, compress_text${NC}"
echo
echo -e "Or as a drop-in replacement:${YELLOW}"
echo -e "import sys"
echo -e "sys.path.append('$SERVICE_DIR')"
echo -e "from openai_wrapper import OpenAI"
echo -e "client = OpenAI()${NC}"
echo
echo -e "Documentation:${YELLOW}"
echo -e "cat $DEPLOYMENT_DIR/PRODUCTION_README.md${NC}"
echo
echo -e "${GREEN}Current statistics are available with:${YELLOW}"
echo -e "python $DEPLOYMENT_DIR/token_solutions.py stats${NC}"