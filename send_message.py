#!/usr/bin/env python3
"""
Send Message utility for the autonomous system
Uses multiple approaches for maximum reliability
Optimized for Telegram with redundant delivery methods
"""
import sys
import os
import time
import json
import datetime
import subprocess

def send_message(message):
    """
    Send a message using multiple methods for reliability
    1. Direct OpenClaw message via Telegram with retries
    2. File-based approach for heartbeat checks
    3. Multiple API fallback methods
    """
    success = False
    errors = []
    
    try:
        # 1. First attempt: Direct OpenClaw message call via Telegram with retries
        for attempt in range(3):  # Try up to 3 times
            try:
                # Add a small delay between retries to avoid rate limiting
                if attempt > 0:
                    time.sleep(2)
                    
                result = subprocess.run([
                    "openclaw", "message", "send",
                    "--channel", "telegram", 
                    "--target", "535786496",
                    "--message", message  # Don't add attempt tracking to avoid spam
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                
                print(f"Message sent via Telegram (attempt {attempt+1})")
                success = True
                break  # Exit the retry loop if successful
            except Exception as e:
                errors.append(f"Telegram delivery attempt {attempt+1} failed: {str(e)}")
                
                # On final attempt failure, try an alternative approach
                if attempt == 2:  
                    try:
                        # Alternative: Try using a direct API call
                        message_json = json.dumps(message)
                        alt_cmd = [
                            "curl", "-s", "-X", "POST", "http://localhost:18789/api/v1/agent/message",
                            "-H", "Content-Type: application/json",
                            "-d", f'{{"channel":"telegram","target":"535786496","message":{message_json}}}'
                        ]
                        subprocess.run(alt_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                        print("Message sent via alternative API method")
                        success = True
                    except Exception as e2:
                        errors.append(f"Alternative delivery method failed: {str(e2)}")
        
        # 2. Create file-based message for heartbeat checks
        try:
            # Create messages directory if it doesn't exist
            messages_dir = os.path.expanduser("~/.openclaw/workspace/autonomous_messages")
            os.makedirs(messages_dir, exist_ok=True)
            
            # Generate a unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            message_file = os.path.join(messages_dir, f"message_{timestamp}.txt")
            
            # Write the message to the file
            with open(message_file, "w") as f:
                f.write(message)
            
            print(f"Message saved to {message_file}")
            
            # Also write to a status file that's easier to find
            status_file = os.path.expanduser("~/.openclaw/workspace/autonomous_status.txt")
            
            with open(status_file, "a") as f:
                f.write(f"\n--- {timestamp} ---\n")
                f.write(message)
                f.write("\n\n")
            
            success = True
        except Exception as e:
            errors.append(f"File storage failed: {str(e)}")
        
        # 3. Try one more API approach as final fallback
        if not success:
            try:
                # Escape quotes in the message for JSON
                message_json = json.dumps(message)
                
                # Use curl with different parameters as final fallback
                curl_cmd = [
                    "curl", "-s", "-m", "15", "-X", "POST", "http://localhost:18789/api/v1/agent/message",
                    "-H", "Content-Type: application/json",
                    "-H", "Accept: application/json",
                    "-d", f'{{"channel":"telegram","target":"535786496","message":{message_json}}}'
                ]
                
                result = subprocess.run(curl_cmd, check=True, capture_output=True, text=True)
                print(f"Message sent via fallback API method")
                success = True
            except Exception as e:
                errors.append(f"Final fallback approach failed: {str(e)}")
        
        # Also log the message for debugging
        log_file = os.path.expanduser("~/.openclaw/workspace/logs/message_delivery.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"\n--- {timestamp} ---\n")
            f.write(f"Message: {message}\n")
            f.write(f"Success: {success}\n")
            if errors:
                f.write(f"Errors: {errors}\n")
            f.write("\n")
        
        return success
    except Exception as e:
        print(f"Failed to send message via all methods: {e}")
        return False

if __name__ == "__main__":
    # Check if message was provided as argument
    if len(sys.argv) > 1:
        message = sys.argv[1]
        send_message(message)
    else:
        # Read from stdin
        message = sys.stdin.read().strip()
        if message:
            send_message(message)
        else:
            print("No message provided")
            sys.exit(1)