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
