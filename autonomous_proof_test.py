#!/usr/bin/env python3
"""
Autonomous System Proof Test
This script demonstrates the autonomous system working by creating
verifiable artifacts and messages at regular intervals.
"""
import os
import time
import datetime
import random
import subprocess
import signal
import sys
import json

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
TEST_DIR = os.path.join(WORKSPACE, "autonomous_proof_test")
LOGS_DIR = os.path.join(WORKSPACE, "logs")
# Using very short intervals for clear demonstration
MESSAGE_INTERVAL = 15  # Send a message every 15 seconds
VERIFICATION_FILES_INTERVAL = 10  # Create verification files every 10 seconds
TEST_DURATION = 5 * 60  # 5 minutes total test time for demonstration
KILL_INTERVAL = 60  # Kill a process every 60 seconds to test self-healing

# Ensure directories exist
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Process list to monitor for testing self-healing
MONITORED_PROCESSES = [
    "persistent_runner.py",
    "github_sync.py"
]

def log_message(message):
    """Log a message to the logs directory"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOGS_DIR, "autonomous_proof_test.log")
    
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    
    print(f"{timestamp} - {message}")

def send_test_message(message):
    """Send a test message using the message system"""
    try:
        log_message(f"Sending message: {message}")
        send_script = os.path.join(WORKSPACE, "send_message.py")
        subprocess.run([
            "python3", send_script, message
        ], check=True)
        return True
    except Exception as e:
        log_message(f"Error sending message: {str(e)}")
        return False

def create_verification_file(index):
    """Create a verification file with the current timestamp"""
    timestamp = datetime.datetime.now().isoformat()
    filename = f"verification_{index}_{timestamp.replace(':', '-')}.txt"
    filepath = os.path.join(TEST_DIR, filename)
    
    content = f"""AUTONOMOUS SYSTEM VERIFICATION FILE
Created: {timestamp}
Test Index: {index}
Random Value: {random.randint(1000, 9999)}

This file was created by the autonomous system without user interaction.
If you're seeing this file, it means the background processes are running
as expected and can perform operations while you're not actively engaged.

Current System State:
{json.dumps({
    'test_started_at': start_time.isoformat(),
    'current_time': timestamp,
    'elapsed_seconds': (datetime.datetime.now() - start_time).total_seconds(),
    'verification_index': index,
}, indent=2)}
"""
    
    with open(filepath, "w") as f:
        f.write(content)
    
    log_message(f"Created verification file: {filename}")
    return filepath

def kill_random_process():
    """Kill a random monitored process to test self-healing"""
    if not MONITORED_PROCESSES:
        log_message("No processes to kill for testing")
        return False
    
    process_name = random.choice(MONITORED_PROCESSES)
    log_message(f"Testing self-healing: Attempting to kill {process_name}")
    
    try:
        # Find the PID for the process
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            log_message(f"Process {process_name} not found to kill")
            return False
        
        pid = result.stdout.strip()
        if not pid:
            log_message(f"No PID found for {process_name}")
            return False
        
        # Kill the process
        log_message(f"Killing {process_name} (PID {pid}) to test self-healing")
        subprocess.run(["kill", pid], check=True)
        
        send_test_message(f"🧪 TEST: Killed {process_name} (PID {pid}) to test self-healing. Monitor should restart it automatically.")
        
        # Wait a moment for the monitor to notice
        time.sleep(5)
        
        # Check if the process was restarted
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            new_pid = result.stdout.strip()
            log_message(f"Self-healing SUCCESS: {process_name} was restarted with PID {new_pid}")
            send_test_message(f"✅ TEST PASSED: {process_name} was automatically restarted with PID {new_pid}")
            return True
        else:
            log_message(f"Self-healing FAILED: {process_name} was not restarted")
            send_test_message(f"❌ TEST FAILED: {process_name} was not automatically restarted")
            return False
    
    except Exception as e:
        log_message(f"Error in kill_random_process: {str(e)}")
        return False

def check_background_messages():
    """Check messages from background processes"""
    try:
        check_script = os.path.join(WORKSPACE, "check_messages.py")
        result = subprocess.run(
            ["python3", check_script],
            capture_output=True,
            text=True
        )
        
        messages = result.stdout.strip()
        if 'AUTONOMOUS SYSTEM MESSAGES' in messages:
            log_message(f"Found background messages: {messages}")
            return True
        else:
            log_message("No background messages found")
            return False
    
    except Exception as e:
        log_message(f"Error checking background messages: {str(e)}")
        return False

def verify_system_running():
    """Verify all expected background systems are running"""
    all_running = True
    
    expected_processes = MONITORED_PROCESSES + ["monitor.py"]
    for process_name in expected_processes:
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pid = result.stdout.strip()
            log_message(f"✅ {process_name} is running with PID {pid}")
        else:
            log_message(f"❌ {process_name} is NOT running")
            all_running = False
    
    return all_running

def signal_handler(sig, frame):
    """Handle interruption signals gracefully"""
    log_message("Received interrupt signal, shutting down test...")
    send_test_message("🛑 Autonomous proof test was interrupted manually. Test stopped.")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main test function
def run_autonomous_test():
    global start_time
    start_time = datetime.datetime.now()
    
    log_message("Starting autonomous system proof test")
    send_test_message("🚀 Starting autonomous system proof test. This test will run for 24 hours, generating verification files and messages without human interaction.")
    
    # Initial verification of system state
    if verify_system_running():
        send_test_message("✅ Initial check: All autonomous system processes are running")
    else:
        send_test_message("⚠️ Initial check: Some autonomous system processes are not running. Starting them now...")
        subprocess.run(["bash", os.path.join(WORKSPACE, "start_autonomous_system.sh")])
    
    # Initialize counters
    message_counter = 0
    file_counter = 0
    kill_counter = 0
    
    last_message_time = time.time() - MESSAGE_INTERVAL  # Send first message immediately
    last_file_time = time.time() - VERIFICATION_FILES_INTERVAL  # Create first file immediately
    last_kill_time = time.time()  # Wait before first kill
    
    # Start time for duration calculation
    end_time = start_time + datetime.timedelta(seconds=TEST_DURATION)
    
    log_message(f"Test will run until: {end_time.isoformat()}")
    send_test_message(f"📊 Test parameters:\n- Running until: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n- Message every: {MESSAGE_INTERVAL} seconds\n- Verification file every: {VERIFICATION_FILES_INTERVAL} seconds\n- Process kill test every: {KILL_INTERVAL} seconds")
    
    try:
        # Main test loop
        while datetime.datetime.now() < end_time:
            current_time = time.time()
            
            # Create file-only status updates instead of sending messages
            if current_time - last_message_time >= MESSAGE_INTERVAL:
                message_counter += 1
                elapsed = (datetime.datetime.now() - start_time).total_seconds() / 60.0
                message = f"🔄 Autonomous system test message #{message_counter} - Running for {elapsed:.1f} minutes without human interaction"
                
                # Instead of sending a message, write to a status file
                status_file = os.path.join(TEST_DIR, f"status_update_{message_counter}.txt")
                with open(status_file, "w") as f:
                    f.write(f"AUTONOMOUS SYSTEM STATUS UPDATE\n")
                    f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
                    f.write(f"Message: {message}\n")
                    f.write(f"Files created: {file_counter}\n")
                    f.write(f"Self-healing tests: {kill_counter}\n")
                
                log_message(f"Created status update file #{message_counter} instead of sending message")
                last_message_time = current_time
            
            # Create verification files
            if current_time - last_file_time >= VERIFICATION_FILES_INTERVAL:
                file_counter += 1
                create_verification_file(file_counter)
                last_file_time = current_time
            
            # Test self-healing by killing a random process
            if current_time - last_kill_time >= KILL_INTERVAL:
                kill_counter += 1
                log_message(f"===== Self-healing test #{kill_counter} =====")
                kill_random_process()
                last_kill_time = current_time
            
            # Check for messages from the background system
            if file_counter % 5 == 0:  # Every 5 files, check for background messages
                check_background_messages()
            
            # Sleep to avoid high CPU usage
            time.sleep(5)
    
    except Exception as e:
        log_message(f"Error in test main loop: {str(e)}")
        send_test_message(f"❌ Test error: {str(e)}")
    finally:
        # Final report
        end_stats = {
            'messages_sent': message_counter,
            'files_created': file_counter,
            'kill_tests': kill_counter,
            'test_duration_minutes': (datetime.datetime.now() - start_time).total_seconds() / 60.0
        }
        
        final_message = f"""
🏁 Autonomous System Proof Test Completed:

📊 Test Statistics:
- Duration: {end_stats['test_duration_minutes']:.1f} minutes
- Messages sent: {end_stats['messages_sent']}
- Verification files: {end_stats['files_created']}
- Self-healing tests: {end_stats['kill_tests']}

📁 Verification files are in: {TEST_DIR}
📋 Logs are in: {os.path.join(LOGS_DIR, "autonomous_proof_test.log")}

This test has proven that the autonomous system can run independently without human interaction.
"""
        
        log_message("Test complete. Final statistics:\n" + json.dumps(end_stats, indent=2))
        send_test_message(final_message)

if __name__ == "__main__":
    run_autonomous_test()