#!/usr/bin/env python3
"""
Test script for the Hourly Memory Summarizer

This script runs the memory summarizer on a test dataset and displays the results.
"""

import os
import sys
import json
import time
from datetime import datetime

# Create test directories if they don't exist
TEST_LOG_DIR = "/Users/karst/.openclaw/workspace/logs/sessions"
TEST_MEMORY_DIR = "/Users/karst/.openclaw/workspace/memory"
TEST_SUMMARY_DIR = os.path.join(TEST_MEMORY_DIR, "hourly-summaries")

os.makedirs(TEST_LOG_DIR, exist_ok=True)
os.makedirs(TEST_MEMORY_DIR, exist_ok=True)
os.makedirs(TEST_SUMMARY_DIR, exist_ok=True)

def create_test_log():
    """Create a test log file with sample conversation data"""
    current_time = time.time()
    
    test_conversation = {
        "session_id": "test-session-123",
        "start_time": current_time - 3600,  # 1 hour ago
        "messages": [
            {
                "role": "user",
                "content": "I need to create a new Kanban system for our team project.",
                "timestamp": current_time - 3500
            },
            {
                "role": "assistant",
                "content": "I can help you set up a Kanban system. Let me understand your requirements first. What kind of project are you working on and how many team members will be using the Kanban board?",
                "timestamp": current_time - 3480
            },
            {
                "role": "user",
                "content": "We're building a software product with 5 team members. We need to track features, bugs, and documentation tasks.",
                "timestamp": current_time - 3450
            },
            {
                "role": "assistant",
                "content": "I'll create a Kanban board with columns for different stages and separate swimlanes for features, bugs, and documentation. Let me set that up for you.",
                "timestamp": current_time - 3400
            },
            {
                "role": "user",
                "content": "We also need to track priorities for each task.",
                "timestamp": current_time - 3380
            },
            {
                "role": "assistant",
                "content": "I'll make sure to include priority levels in the Kanban setup. I'll use high, medium, and low priorities with color coding for better visibility. I decided to use a JSON file for storing the Kanban data so it can be easily modified and extended.",
                "timestamp": current_time - 3350
            },
            {
                "role": "user",
                "content": "Great! Let's implement it. Also, we need to make sure we can integrate it with our existing GitHub workflow.",
                "timestamp": current_time - 3300
            },
            {
                "role": "assistant",
                "content": "I'll implement the Kanban system with GitHub integration. The action items for this project are: 1) Create the basic Kanban structure, 2) Add priority tracking, 3) Implement GitHub integration, 4) Set up automated movement of cards based on GitHub actions. Let me get started on this right away.",
                "timestamp": current_time - 3250
            }
        ]
    }
    
    # Save test data to a log file
    log_file_path = os.path.join(TEST_LOG_DIR, f"test-session-{int(current_time)}.json")
    with open(log_file_path, 'w') as f:
        json.dump(test_conversation, f)
    
    print(f"Created test log file at {log_file_path}")
    return log_file_path

def run_test():
    """Run the memory summarizer on test data"""
    # Import after creating directories to avoid import errors
    import importlib.util
    spec = importlib.util.spec_from_file_location("hourly_memory_summarizer", 
                                                 "/Users/karst/.openclaw/workspace/hourly-memory-summarizer.py")
    hourly_memory_summarizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hourly_memory_summarizer)
    ConversationSummarizer = hourly_memory_summarizer.ConversationSummarizer
    
    # Create test data
    create_test_log()
    
    # Run the summarizer
    print("Running hourly memory summarizer...")
    summarizer = ConversationSummarizer()
    result = summarizer.run(hour=datetime.now().hour, hours_back=1)
    
    if result:
        print("\n=== Summary Results ===")
        print(f"Hourly summary saved to: {result['hourly_path']}")
        print(f"Daily summary updated at: {result['daily_path']}")
        print("\nStatistics:")
        for key, value in result['stats'].items():
            print(f"  {key}: {value}")
        print("\nTopics:")
        print(f"  {', '.join(result['topics'])}")
        
        # Display the generated summary
        print("\n=== Generated Summary Content ===")
        with open(result['hourly_path'], 'r') as f:
            print(f.read())
    else:
        print("No results returned from summarizer")

if __name__ == "__main__":
    run_test()