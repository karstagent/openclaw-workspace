#!/usr/bin/env python3
"""
Check Messages utility for the autonomous system
Checks for messages from background processes during heartbeats
"""
import os
import datetime
import glob

def check_messages():
    """
    Check for messages from background processes
    """
    # Define the directory where messages are stored
    messages_dir = os.path.expanduser("~/.openclaw/workspace/autonomous_messages")
    
    # Create the directory if it doesn't exist
    os.makedirs(messages_dir, exist_ok=True)
    
    # Look for message files
    message_files = sorted(glob.glob(os.path.join(messages_dir, "message_*.txt")))
    
    if not message_files:
        print("No new messages found")
        return None
    
    # Read all messages
    messages = []
    for message_file in message_files:
        try:
            with open(message_file, "r") as f:
                content = f.read().strip()
                
            messages.append(content)
            
            # Delete the file after reading
            os.remove(message_file)
        except Exception as e:
            print(f"Error reading {message_file}: {e}")
    
    if not messages:
        print("No valid messages found")
        return None
    
    # Combine messages if there are multiple
    if len(messages) == 1:
        return messages[0]
    else:
        combined = "📬 Multiple Autonomous System Messages:\n\n"
        for i, msg in enumerate(messages, 1):
            combined += f"--- Message {i} ---\n{msg}\n\n"
        return combined

if __name__ == "__main__":
    message = check_messages()
    if message:
        print("\n=== AUTONOMOUS SYSTEM MESSAGES ===\n")
        print(message)
        print("\n=================================\n")
    else:
        print("No autonomous system messages")