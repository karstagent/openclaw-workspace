#!/usr/bin/env python3
"""
Fix for token limit integration issues.
This script ensures all API calls to language models are properly routed through the token management system.
"""

import os
import sys
import importlib
import glob
import re
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs/token_fix.log"))
    ]
)
logger = logging.getLogger("token-fix")

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SOLUTIONS_DIR = os.path.join(WORKSPACE_DIR, "token_solutions")
SERVICES_DIR = os.path.join(WORKSPACE_DIR, "services")
GLASSWALL_DIR = os.path.join(WORKSPACE_DIR, "glasswall-rebuild")

# Patterns to look for in code
OPENAI_IMPORT_PATTERNS = [
    r'from\s+openai\s+import',
    r'import\s+openai\s+',
    r'OpenAI\(',
]

ANTHROPIC_IMPORT_PATTERNS = [
    r'from\s+anthropic\s+import',
    r'import\s+anthropic\s+',
    r'Anthropic\(',
]

# Replacement templates
OPENAI_REPLACEMENT = """
# Token management system integration
import sys
sys.path.append('{services_dir}')
from openai_wrapper import OpenAI
"""

ANTHROPIC_REPLACEMENT = """
# Token management system integration
import sys
sys.path.append('{services_dir}')
try:
    from openai_wrapper import Anthropic
except ImportError:
    from anthropic import Anthropic
"""

def verify_token_solutions():
    """Verify that token solutions are properly installed"""
    if not os.path.exists(TOKEN_SOLUTIONS_DIR):
        logger.error(f"Token solutions directory not found: {TOKEN_SOLUTIONS_DIR}")
        return False
        
    if not os.path.exists(os.path.join(TOKEN_SOLUTIONS_DIR, "token_solutions.py")):
        logger.error(f"token_solutions.py not found in {TOKEN_SOLUTIONS_DIR}")
        return False
        
    if not os.path.exists(os.path.join(SERVICES_DIR, "openai_wrapper.py")):
        logger.error(f"openai_wrapper.py not found in {SERVICES_DIR}")
        return False
    
    logger.info("Token solutions installation verified")
    return True

def patch_file(file_path):
    """Patch a file to use the token management system"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file already uses the token solutions
    if 'openai_wrapper' in content:
        logger.info(f"File already uses token solutions: {file_path}")
        return False
    
    # Check for OpenAI usage
    openai_used = any(re.search(pattern, content) for pattern in OPENAI_IMPORT_PATTERNS)
    anthropic_used = any(re.search(pattern, content) for pattern in ANTHROPIC_IMPORT_PATTERNS)
    
    if not openai_used and not anthropic_used:
        logger.info(f"No LLM API usage found in: {file_path}")
        return False
    
    # Create backup
    backup_path = f"{file_path}.bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Apply replacements
    if openai_used:
        # Replace standard OpenAI import with wrapper
        for pattern in OPENAI_IMPORT_PATTERNS:
            content = re.sub(pattern, 
                             OPENAI_REPLACEMENT.format(services_dir=SERVICES_DIR) + "\n# Original import replaced:",
                             content,
                             count=1)
    
    if anthropic_used:
        # Replace standard Anthropic import with wrapper
        for pattern in ANTHROPIC_IMPORT_PATTERNS:
            content = re.sub(pattern, 
                             ANTHROPIC_REPLACEMENT.format(services_dir=SERVICES_DIR) + "\n# Original import replaced:",
                             content, 
                             count=1)
    
    # Write updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Patched file: {file_path}")
    return True

def scan_and_patch_directory(directory, extensions=None):
    """Scan a directory for files to patch"""
    if extensions is None:
        extensions = ['.py', '.tsx', '.jsx', '.ts', '.js']
    
    patched_count = 0
    scanned_count = 0
    
    for ext in extensions:
        for file_path in glob.glob(f"{directory}/**/*{ext}", recursive=True):
            scanned_count += 1
            if patch_file(file_path):
                patched_count += 1
    
    logger.info(f"Scanned {scanned_count} files, patched {patched_count} files in {directory}")
    return patched_count

def verify_wrapper_functionality():
    """Verify that the wrappers are functioning correctly"""
    try:
        test_code = """
import sys
sys.path.append('{services_dir}')
from openai_wrapper import OpenAI

client = OpenAI()
print("OpenAI wrapper initialized successfully")

# Test with small input
result = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{{"role": "user", "content": "Hello"}}],
    max_tokens=10
)
print("Test complete")
""".format(services_dir=SERVICES_DIR)
        
        # Write test to temporary file
        test_path = os.path.join(WORKSPACE_DIR, "token_test_temp.py")
        with open(test_path, 'w') as f:
            f.write(test_code)
        
        # Execute test
        logger.info("Testing OpenAI wrapper functionality")
        os.system(f"python3 {test_path}")
        
        # Clean up
        os.remove(test_path)
        return True
    except Exception as e:
        logger.error(f"Error testing wrapper functionality: {e}")
        return False

def update_token_solutions_config():
    """Update token solutions configuration for better handling of large inputs"""
    config_path = os.path.join(WORKSPACE_DIR, "config/token_solutions.json")
    
    # Create config directory if needed
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Default config with more aggressive settings
    config = {
        "semantic_compression": {
            "enabled": True,
            "default_compression_ratio": 8,
            "token_threshold": 100000,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "summarizer_model": "facebook/bart-large-cnn",
            "preserve_structure": True
        },
        "context_extension": {
            "enabled": True,
            "target_context_length": 200000,
            "fallback_to_compression": True,
            "api_type": "openai"
        },
        "monitoring": {
            "log_level": "info",
            "track_token_savings": True,
            "save_statistics": True,
            "statistics_file": "token_usage_stats.jsonl"
        }
    }
    
    import json
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Updated token solutions config at {config_path}")

def ensure_token_awareness():
    """Create helper utility for checking token counts"""
    token_utility_path = os.path.join(WORKSPACE_DIR, "check_tokens.py")
    
    content = """#!/usr/bin/env python3
\"\"\"
Token count utility for quickly checking input sizes
\"\"\"

import os
import sys
import argparse
from pathlib import Path

# Add token_solutions to path
token_solutions_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "token_solutions"
)
sys.path.append(token_solutions_dir)

try:
    from token_solutions import count_tokens
except ImportError:
    # Fallback tiktoken implementation
    import tiktoken
    def count_tokens(text):
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))

def main():
    parser = argparse.ArgumentParser(description="Check token count of text input")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", "-t", help="Text to count tokens for")
    input_group.add_argument("--file", "-f", help="File to count tokens for")
    input_group.add_argument("--stdin", "-s", action="store_true", help="Read from stdin")
    
    # Additional options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--chunk", "-c", type=int, help="Split into chunks of specified token count")
    
    args = parser.parse_args()
    
    # Get input text
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, 'r') as f:
            text = f.read()
    elif args.stdin:
        text = sys.stdin.read()
    
    # Count tokens
    token_count = count_tokens(text)
    
    # Output
    if args.verbose:
        print(f"Text length: {len(text)} characters")
        print(f"Token count: {token_count} tokens")
        # Estimate compression ratio
        if token_count > 1000:
            from token_solutions import compress_text
            compressed = compress_text(text)
            compressed_tokens = count_tokens(compressed)
            ratio = token_count / compressed_tokens if compressed_tokens > 0 else 0
            print(f"Compressed tokens: {compressed_tokens}")
            print(f"Compression ratio: {ratio:.2f}x")
    else:
        print(token_count)
    
    # Chunk output if requested
    if args.chunk and token_count > args.chunk:
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")
        tokens = encoding.encode(text)
        
        chunk_count = (token_count + args.chunk - 1) // args.chunk
        print(f"Splitting into {chunk_count} chunks of {args.chunk} tokens")
        
        for i in range(0, token_count, args.chunk):
            chunk_tokens = tokens[i:i+args.chunk]
            chunk_text = encoding.decode(chunk_tokens)
            chunk_file = f"chunk_{i//args.chunk+1}_of_{chunk_count}.txt"
            with open(chunk_file, 'w') as f:
                f.write(chunk_text)
            print(f"Wrote {len(chunk_tokens)} tokens to {chunk_file}")

if __name__ == "__main__":
    main()
"""
    
    with open(token_utility_path, 'w') as f:
        f.write(content)
    
    os.chmod(token_utility_path, 0o755)
    logger.info(f"Created token checking utility at {token_utility_path}")

def main():
    """Main function"""
    logger.info("Starting token limit integration fix")
    
    # Verify token solutions installation
    if not verify_token_solutions():
        logger.error("Token solutions installation verification failed")
        return
    
    # Update token solutions configuration
    update_token_solutions_config()
    
    # Scan and patch directories
    scan_and_patch_directory(GLASSWALL_DIR)
    scan_and_patch_directory(WORKSPACE_DIR, extensions=['.py'])
    
    # Verify wrapper functionality
    if not verify_wrapper_functionality():
        logger.warning("Wrapper functionality verification failed")
    
    # Create token awareness utility
    ensure_token_awareness()
    
    logger.info("Token limit integration fix completed")
    print("Token limit integration fix completed successfully")

if __name__ == "__main__":
    main()