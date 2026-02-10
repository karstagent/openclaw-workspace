#!/usr/bin/env python3
"""
API Integration Layer for Semantic Compression
Provides transparent compression for LLM API requests.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Union, Callable
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api-integration")

# Check for semantic_compression module
try:
    from semantic_compression import SemanticCompressor, count_tokens
except ImportError:
    logger.error("semantic_compression module not found. Please ensure it's in the same directory or PYTHONPATH.")
    sys.exit(1)

class CompressionEnabledClient:
    """
    Wrapper for LLM API clients that transparently applies semantic compression
    when requests exceed token limits.
    
    Currently supports:
    - OpenAI API
    - Anthropic API
    - Generic API proxy
    """
    
    def __init__(
        self,
        compression_ratio: int = 6,
        token_limit_threshold: int = 150000,
        max_output_tokens: int = 32000,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        summarizer_model: str = "facebook/bart-large-cnn",
        device: str = None,
        verbose: bool = False,
        original_client = None
    ):
        """
        Initialize the compression-enabled client.
        
        Args:
            compression_ratio: Target compression ratio (higher = more compression)
            token_limit_threshold: Token count threshold to trigger compression
            max_output_tokens: Maximum tokens to reserve for output
            embedding_model: Model to use for text embeddings
            summarizer_model: Model to use for summarization
            device: Device to use for compression (cuda or cpu)
            verbose: Enable verbose logging
            original_client: Original API client to wrap
        """
        self.compression_ratio = compression_ratio
        self.token_limit_threshold = token_limit_threshold
        self.max_output_tokens = max_output_tokens
        self.verbose = verbose
        self._original_client = original_client
        
        # Set logging level based on verbosity
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize the compressor lazily to avoid loading models until needed
        self._compressor = None
        self._embedding_model = embedding_model
        self._summarizer_model = summarizer_model
        self._device = device
        
        logger.info(f"Initialized compression-enabled client with {compression_ratio}x ratio")
        logger.info(f"Will compress messages exceeding {token_limit_threshold} tokens")
    
    def _get_compressor(self):
        """Lazy-load the compressor when needed."""
        if self._compressor is None:
            logger.info("Initializing semantic compressor...")
            self._compressor = SemanticCompressor(
                embedding_model=self._embedding_model,
                summarizer_model=self._summarizer_model,
                device=self._device
            )
        return self._compressor
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count for a text string."""
        # Use the actual count_tokens function from semantic_compression
        return count_tokens(text)
    
    def _compress_message_content(self, content: str) -> str:
        """Apply semantic compression to message content."""
        compressor = self._get_compressor()
        
        # Log original token count
        original_tokens = self._estimate_token_count(content)
        logger.info(f"Compressing message with {original_tokens} tokens")
        
        # Apply compression
        start_time = time.time()
        compressed_content = compressor.compress(
            content, 
            compression_ratio=self.compression_ratio
        )
        elapsed_time = time.time() - start_time
        
        # Log compression results
        compressed_tokens = self._estimate_token_count(compressed_content)
        actual_ratio = original_tokens / max(1, compressed_tokens)
        logger.info(f"Compressed to {compressed_tokens} tokens (ratio: {actual_ratio:.2f}x)")
        logger.info(f"Compression took {elapsed_time:.2f} seconds")
        
        return compressed_content
    
    def _process_openai_messages(self, messages: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], bool]:
        """Process OpenAI-style messages, compressing if needed."""
        total_tokens = sum(self._estimate_token_count(msg.get('content', '')) 
                          for msg in messages)
        
        # Check if compression is needed
        if total_tokens <= self.token_limit_threshold:
            logger.info(f"Messages under threshold ({total_tokens} tokens), no compression needed")
            return messages, False
        
        # Apply compression to user messages only
        compressed_messages = []
        was_compressed = False
        
        for msg in messages:
            if msg.get('role') == 'user' and msg.get('content'):
                content = msg.get('content', '')
                tokens = self._estimate_token_count(content)
                
                # Only compress long messages
                if tokens > 1000:  # Don't compress short messages
                    compressed_content = self._compress_message_content(content)
                    compressed_msg = msg.copy()
                    compressed_msg['content'] = compressed_content
                    compressed_messages.append(compressed_msg)
                    was_compressed = True
                else:
                    compressed_messages.append(msg)
            else:
                compressed_messages.append(msg)
        
        return compressed_messages, was_compressed
    
    def _create_compression_notice(self) -> Dict[str, str]:
        """Create a system message noting that compression was applied."""
        return {
            "role": "system", 
            "content": "Note: This request was automatically compressed using semantic compression to fit within the model's context window. Some details may have been summarized."
        }

    # === OpenAI API Integration ===
    
    def chat_completions_create(self, **kwargs):
        """OpenAI-compatible chat completions with compression."""
        if self._original_client is None:
            try:
                
# Token management system integration
import sys
sys.path.append('/Users/karst/.openclaw/workspace/services')
from openai_wrapper import OpenAI

# Original import replaced: OpenAI
                self._original_client = 
# Token management system integration
import sys
sys.path.append('/Users/karst/.openclaw/workspace/services')
from openai_wrapper import OpenAI

# Original import replaced:)
                logger.info("Initialized OpenAI client")
            except ImportError:
                logger.error("OpenAI client not found. Please install with: pip install openai")
                raise
        
        # Extract messages
        messages = kwargs.get('messages', [])
        
        # Process messages
        compressed_messages, was_compressed = self._process_openai_messages(messages)
        
        # Add compression notice if needed
        if was_compressed and kwargs.get('add_compression_notice', True):
            compressed_messages.insert(0, self._create_compression_notice())
        
        # Update kwargs
        new_kwargs = kwargs.copy()
        new_kwargs['messages'] = compressed_messages
        
        # Call original OpenAI client
        return self._original_client.chat.completions.create(**new_kwargs)
    
    # === Anthropic API Integration ===
    
    def messages_create(self, **kwargs):
        """Anthropic-compatible messages API with compression."""
        if self._original_client is None:
            try:
                
# Token management system integration
import sys
sys.path.append('/Users/karst/.openclaw/workspace/services')
try:
    from openai_wrapper import Anthropic
except ImportError:
    from anthropic import Anthropic

# Original import replaced: Anthropic
                self._original_client = 
# Token management system integration
import sys
sys.path.append('/Users/karst/.openclaw/workspace/services')
try:
    from openai_wrapper import Anthropic
except ImportError:
    from anthropic import Anthropic

# Original import replaced:)
                logger.info("Initialized Anthropic client")
            except ImportError:
                logger.error("Anthropic client not found. Please install with: pip install anthropic")
                raise
        
        # For Anthropic, we need to handle the different message format
        messages = kwargs.get('messages', [])
        
        # Process messages
        compressed_messages, was_compressed = self._process_openai_messages(messages)
        
        # Add compression notice if needed
        if was_compressed and kwargs.get('add_compression_notice', True):
            compressed_messages.insert(0, {"role": "user", "content": "I'm sending a compressed version of my content to fit in your context window."})
            compressed_messages.insert(1, {"role": "assistant", "content": "I understand. I'll work with your compressed content. Some details might have been summarized, but I'll do my best to help."})
        
        # Update kwargs
        new_kwargs = kwargs.copy()
        new_kwargs['messages'] = compressed_messages
        
        # Call original Anthropic client
        return self._original_client.messages.create(**new_kwargs)
    
    # === Generic API Proxy ===
    
    def proxy_request(self, request_function: Callable, messages_key: str = 'messages', **kwargs):
        """
        Generic proxy for any API that uses a message-based format.
        
        Args:
            request_function: Function to call for the actual API request
            messages_key: Key in kwargs that contains messages
            **kwargs: Arguments to pass to request_function
        """
        # Extract messages
        messages = kwargs.get(messages_key, [])
        
        # Process messages
        compressed_messages, was_compressed = self._process_openai_messages(messages)
        
        # Update kwargs
        new_kwargs = kwargs.copy()
        new_kwargs[messages_key] = compressed_messages
        
        # Call the provided request function
        return request_function(**new_kwargs)

# Command-line interface for testing
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the compression-enabled API client")
    parser.add_argument("--input", "-i", required=True, help="Input file containing messages")
    parser.add_argument("--output", "-o", help="Output file for compressed messages")
    parser.add_argument("--ratio", "-r", type=int, default=6, help="Compression ratio (default: 6)")
    parser.add_argument("--threshold", "-t", type=int, default=150000, help="Token threshold (default: 150000)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize client
    client = CompressionEnabledClient(
        compression_ratio=args.ratio,
        token_limit_threshold=args.threshold,
        verbose=args.verbose
    )
    
    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        if args.input.endswith('.json'):
            messages = json.load(f)
        else:
            # Assume it's a single user message
            messages = [{"role": "user", "content": f.read()}]
    
    # Process messages
    compressed_messages, was_compressed = client._process_openai_messages(messages)
    
    # Output result
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(compressed_messages, f, indent=2)
        print(f"Compressed messages written to {args.output}")
    else:
        print(json.dumps(compressed_messages, indent=2))

if __name__ == "__main__":
    main()