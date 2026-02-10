#!/usr/bin/env python3
"""
Test script for the OpenClaw context management system.
This script generates a sample request that would exceed context limits,
then demonstrates how our context manager handles it.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from openclaw_context_handler import OpenClawContextHandler

def generate_test_request(message_count=200, content_length=500, max_tokens=32000):
    """
    Generate a test request with a specified number of messages and content length.
    
    Args:
        message_count: Number of messages to generate
        content_length: Average length of each message in characters
        max_tokens: Maximum tokens for response
        
    Returns:
        Dictionary containing the test request
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides detailed responses."}
    ]
    
    # Generate alternating user/assistant messages
    for i in range(message_count):
        if i % 2 == 0:
            # User message
            content = f"This is user message {i}. " + "A" * content_length
            messages.append({"role": "user", "content": content})
        else:
            # Assistant message
            content = f"This is assistant response {i}. " + "B" * content_length
            messages.append({"role": "assistant", "content": content})
    
    # Create request
    request = {
        "model": "openrouter/anthropic/claude-3-opus",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    return request

def calculate_token_estimate(request):
    """
    Calculate a rough estimate of tokens in the request.
    
    Args:
        request: Request dictionary with messages
        
    Returns:
        Tuple of (estimated input tokens, max_tokens, total tokens)
    """
    # Rough estimation: 4 chars ≈ 1 token
    input_tokens = 0
    for msg in request.get("messages", []):
        content = msg.get("content", "")
        input_tokens += len(content) // 4
    
    max_tokens = request.get("max_tokens", 32000)
    total = input_tokens + max_tokens
    
    return input_tokens, max_tokens, total

def main():
    """Main function to run the test"""
    # Generate a test request that would exceed context limits
    request = generate_test_request(message_count=400, content_length=2000, max_tokens=32000)
    
    # Calculate token estimates
    input_tokens, max_tokens, total = calculate_token_estimate(request)
    print(f"Original request:")
    print(f"- Messages: {len(request['messages'])}")
    print(f"- Estimated input tokens: {input_tokens}")
    print(f"- Max output tokens: {max_tokens}")
    print(f"- Estimated total tokens: {total}")
    print()
    
    # Initialize context handler
    handler = OpenClawContextHandler()
    
    # Process the request
    processed = handler.process_request(request)
    
    # Calculate processed token estimates
    proc_input, proc_max, proc_total = calculate_token_estimate(processed)
    print(f"Processed request:")
    print(f"- Messages: {len(processed['messages'])}")
    print(f"- Estimated input tokens: {proc_input}")
    print(f"- Max output tokens: {proc_max}")
    print(f"- Estimated total tokens: {proc_total}")
    print()
    
    # Check if context issue was resolved
    if proc_total <= 200000:
        print("✅ Context management successful: Total tokens now within 200K limit")
    else:
        print("❌ Context management failed: Total tokens still exceed 200K limit")
    
    # Show message reduction details
    if len(processed["messages"]) < len(request["messages"]):
        removed = len(request["messages"]) - len(processed["messages"])
        print(f"- Removed {removed} messages ({removed/len(request['messages'])*100:.1f}%)")
    
    # Show max_tokens reduction details
    if processed.get("max_tokens") < request.get("max_tokens"):
        token_reduction = request.get("max_tokens") - processed.get("max_tokens")
        print(f"- Reduced max_tokens by {token_reduction}")
    
    # Calculate total token reduction
    total_reduction = total - proc_total
    print(f"- Total token reduction: {total_reduction} ({total_reduction/total*100:.1f}%)")
    
    # Output the first 3 and last 3 messages to see what was kept
    print("\nFirst 3 messages after processing:")
    for i, msg in enumerate(processed["messages"][:3]):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", "")
        print(f"{i}. [{role}] {content}")
    
    print("\nLast 3 messages after processing:")
    for i, msg in enumerate(processed["messages"][-3:]):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", "")
        print(f"{len(processed['messages'])-3+i}. [{role}] {content}")

if __name__ == "__main__":
    main()