#!/usr/bin/env python3
"""
Test script for semantic compression with a sample document
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("compression-test")

# Attempt to import the compression modules
try:
    from semantic_compression import SemanticCompressor, count_tokens
except ImportError:
    logger.error("semantic_compression module not found. Please run setup_compression.sh first.")
    sys.exit(1)

# Sample text for testing (a repeating pattern to create a long document)
SAMPLE_TEXT = """
Language models have revolutionized natural language processing with their ability to understand and generate human-like text. 
However, they face significant limitations when processing long documents due to fixed context window constraints. 
These constraints arise from the self-attention mechanism in transformer architectures, which scales quadratically with input length.
As documents grow longer, models struggle to maintain coherence and accuracy across the entire text.

Several approaches have emerged to address these limitations:
1. Architectural innovations that reduce the computational complexity of attention mechanisms
2. Position encoding adaptations that enable generalization to longer sequences
3. Semantic compression techniques that reduce redundancy while preserving meaning
4. Hybrid retrieval methods that dynamically manage context windows

The trade-offs between these approaches involve computational efficiency, implementation complexity, and preservation of semantic content.
When working with extremely long documents, practitioners must carefully consider which strategy best suits their specific use case.
"""

def create_long_document(base_text, repetitions=100, variations=True):
    """Create a long document by repeating text with optional variations."""
    document = []
    
    for i in range(repetitions):
        if variations and i % 10 == 0:
            # Add some variations every 10 repetitions
            document.append(f"Section {i+1}: The following content discusses language model limitations.")
        
        # Add the base text with occasional minor variations
        if variations and i % 3 == 0:
            # Replace some words to create variations
            modified_text = base_text.replace("language models", "large language models")
            modified_text = modified_text.replace("context window", "token context window")
            document.append(modified_text)
        else:
            document.append(base_text)
            
        # Add occasional examples or details
        if variations and i % 7 == 0:
            document.append("""
            For example, when processing a technical manual with 500 pages, traditional models might:
            - Lose track of topics discussed in early chapters
            - Miss cross-references between distant sections
            - Fail to maintain consistent terminology throughout the document
            - Generate contradictory statements based on partial context
            """)
    
    return "\n\n".join(document)

def main():
    # Create a test directory if it doesn't exist
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_compression")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a long document
    logger.info("Creating test document...")
    document = create_long_document(SAMPLE_TEXT, repetitions=200)
    
    # Save the original document
    original_path = os.path.join(test_dir, "original_document.txt")
    with open(original_path, "w", encoding="utf-8") as f:
        f.write(document)
    
    # Count tokens in original document
    original_tokens = count_tokens(document)
    logger.info(f"Original document: {len(document)} characters, {original_tokens} tokens")
    
    # Initialize the compressor
    logger.info("Initializing semantic compressor...")
    compressor = SemanticCompressor()
    
    # Test different compression ratios
    compression_ratios = [3, 6, 9]
    
    for ratio in compression_ratios:
        logger.info(f"Testing compression ratio {ratio}...")
        
        # Measure compression time
        start_time = time.time()
        compressed = compressor.compress(document, compression_ratio=ratio)
        elapsed_time = time.time() - start_time
        
        # Save compressed document
        compressed_path = os.path.join(test_dir, f"compressed_ratio_{ratio}.txt")
        with open(compressed_path, "w", encoding="utf-8") as f:
            f.write(compressed)
        
        # Calculate statistics
        compressed_tokens = count_tokens(compressed)
        actual_ratio = original_tokens / compressed_tokens
        
        logger.info(f"Compression ratio {ratio}: {len(compressed)} characters, {compressed_tokens} tokens")
        logger.info(f"Actual compression ratio: {actual_ratio:.2f}x")
        logger.info(f"Compression took {elapsed_time:.2f} seconds")
        
        # Print sample of compressed text
        preview_length = min(500, len(compressed))
        logger.info(f"Sample of compressed text (ratio {ratio}):")
        logger.info(compressed[:preview_length] + "...")
        logger.info("-" * 40)
    
    logger.info(f"All test results saved to {test_dir}")
    logger.info(f"Original document: {original_path}")
    for ratio in compression_ratios:
        logger.info(f"Compressed ({ratio}x): {os.path.join(test_dir, f'compressed_ratio_{ratio}.txt')}")

if __name__ == "__main__":
    main()