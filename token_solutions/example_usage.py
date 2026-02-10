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
