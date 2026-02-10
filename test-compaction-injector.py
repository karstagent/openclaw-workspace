#!/usr/bin/env python3
"""
Test script for Post-Compaction Context Injector

This script runs a test of the post-compaction context injector by simulating
a compaction event and displaying the resulting injection.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
import random

# Create test directories if they don't exist
TEST_LOG_DIR = "/Users/karst/.openclaw/workspace/logs/sessions"
TEST_MEMORY_DIR = "/Users/karst/.openclaw/workspace/memory"
TEST_SUMMARY_DIR = os.path.join(TEST_MEMORY_DIR, "hourly-summaries")

os.makedirs(TEST_LOG_DIR, exist_ok=True)
os.makedirs(TEST_MEMORY_DIR, exist_ok=True)
os.makedirs(TEST_SUMMARY_DIR, exist_ok=True)

def create_test_data():
    """Create test data for compaction detection testing"""
    # Create a test session log
    session_id = f"test-session-{int(time.time())}"
    current_time = time.time()
    
    # Create a sequence of messages
    messages = []
    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        message_time = current_time - (10 - i) * 60  # 1 minute apart
        
        content = ""
        if role == "user":
            content = random.choice([
                "What's the status of our project?",
                "Can you summarize what we've done so far?",
                "I need to add a new feature to the system",
                "What was the decision we made about the database?",
                "Remind me of the API endpoints we planned"
            ])
        else:
            content = random.choice([
                "The project is progressing well. We've completed the planning phase.",
                "So far we've designed the architecture and defined the API endpoints.",
                "I can help you add that feature. What specifically do you need?",
                "We decided to use PostgreSQL for the database with a connection pool.",
                "The API endpoints include /api/auth, /api/users, and /api/messages."
            ])
        
        messages.append({
            "id": f"msg_{i}",
            "role": role,
            "content": content,
            "timestamp": datetime.fromtimestamp(message_time).isoformat()
        })
    
    # Create a system message that might appear after compaction
    compaction_message = {
        "id": "msg_compaction",
        "role": "system",
        "content": "Context has been refreshed. Previous messages may no longer be available.",
        "timestamp": datetime.fromtimestamp(current_time).isoformat()
    }
    
    # Save the test session
    session_data = {
        "session_id": session_id,
        "start_time": datetime.fromtimestamp(current_time - 3600).isoformat(),
        "messages": messages
    }
    
    log_path = os.path.join(TEST_LOG_DIR, f"{session_id}.json")
    with open(log_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return {
        "session_id": session_id,
        "log_path": log_path,
        "messages": messages,
        "compaction_message": compaction_message
    }

def test_compaction_detection():
    """Test the compaction detection logic"""
    print("Testing compaction detection...")
    
    # Import the compaction injector module using direct import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "post_compaction_injector", 
        "/Users/karst/.openclaw/workspace/post-compaction-inject.py"
    )
    post_compaction_injector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(post_compaction_injector)
    ContextStateManager = post_compaction_injector.ContextStateManager
    
    # Create a test state manager
    state_manager = ContextStateManager(state_file="test-context-state.json")
    
    # Create test data
    test_data = create_test_data()
    session_id = test_data["session_id"]
    
    print(f"Created test session: {session_id}")
    
    # Register the initial messages
    for msg in test_data["messages"]:
        state_manager.register_message(
            session_id=session_id,
            message_id=msg["id"],
            content=msg["content"],
            role=msg["role"],
            timestamp=msg["timestamp"]
        )
    
    print(f"Registered {len(test_data['messages'])} test messages")
    
    # Test compaction detection
    compaction_msg = test_data["compaction_message"]
    detected = state_manager.detect_compaction(
        session_id=session_id,
        message_id=compaction_msg["id"],
        content=compaction_msg["content"],
        role=compaction_msg["role"]
    )
    
    print(f"Compaction detected: {detected}")
    
    # Clean up test state file
    if os.path.exists("test-context-state.json"):
        os.remove("test-context-state.json")
    
    return detected

def test_injection_generation():
    """Test the context injection generation"""
    print("\nTesting context injection generation...")
    
    # Import the compaction injector module using direct import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "post_compaction_injector", 
        "/Users/karst/.openclaw/workspace/post-compaction-inject.py"
    )
    post_compaction_injector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(post_compaction_injector)
    MemoryRetriever = post_compaction_injector.MemoryRetriever
    
    # Create the memory retriever
    memory_retriever = MemoryRetriever()
    
    # Generate an injection
    session_id = f"test-session-{int(time.time())}"
    injection = memory_retriever.generate_context_injection(
        session_id=session_id,
        detected_compaction=True
    )
    
    print("\n=== Context Injection Content ===\n")
    print(injection)
    
    # Show the summary files used
    summaries = memory_retriever.get_recent_summaries()
    daily_memories = memory_retriever.get_daily_memory()
    
    print("\n=== Memory Sources ===\n")
    print(f"Recent summaries: {len(summaries)}")
    for summary in summaries:
        print(f"  - {summary['date']} {summary['time']} ({os.path.basename(summary['path'])})")
    
    print(f"\nDaily memories: {len(daily_memories)}")
    for memory in daily_memories:
        print(f"  - {memory['date']} ({os.path.basename(memory['path'])})")
    
    return injection

def run_test():
    """Run the full test suite"""
    print("=== Post-Compaction Context Injector Tests ===\n")
    
    # Run the individual tests
    compaction_detected = test_compaction_detection()
    injection = test_injection_generation()
    
    # Run a simulated full process
    print("\n=== Running Simulated Compaction Handler ===\n")
    
    # Use the CLI simulation mode
    os.system("python3 post-compaction-inject.py --simulate")

if __name__ == "__main__":
    run_test()