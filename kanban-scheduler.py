#!/usr/bin/env python3

import os
import json
import time
import datetime
import subprocess
import threading
import logging

# Configure logging
logging.basicConfig(
    filename='/Users/karst/.openclaw/workspace/logs/kanban-scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('kanban-scheduler')

class KanbanScheduler:
    def __init__(self):
        self.base_path = '/Users/karst/.openclaw/workspace'
        self.kanban_file = os.path.join(self.base_path, 'kanban-board.json')
        self.message_file = os.path.join(self.base_path, 'kanban-update-message.txt')
        self.interval_minutes = 5  # Run every 5 minutes
        self._stop_event = threading.Event()

    def run_forever(self):
        """Run the scheduler in an infinite loop until stopped"""
        logger.info("Starting Kanban scheduler...")
        
        try:
            while not self._stop_event.is_set():
                self.check_and_update()
                
                # Sleep until next interval (check every second if we should stop)
                for _ in range(self.interval_minutes * 60):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
        
        logger.info("Kanban scheduler stopped.")

    def stop(self):
        """Stop the scheduler"""
        self._stop_event.set()

    def check_and_update(self):
        """Run a Kanban update check"""
        logger.info("Running Kanban update check...")
        
        try:
            # Get current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get in-progress task info
            task_info = self.get_in_progress_task()
            
            # Create the update message
            message = f"🔄 AUTOMATED KANBAN UPDATE ({timestamp}):\n{task_info}\nNext update in {self.interval_minutes} minutes."
            
            # Save the message to a file
            with open(self.message_file, 'w') as f:
                f.write(message)
            
            # Send the message via Telegram
            self.send_telegram_message(message)
            
            logger.info("Kanban update completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error during Kanban update: {e}")
            return False

    def get_in_progress_task(self):
        """Get information about the current in-progress task"""
        try:
            with open(self.kanban_file, 'r') as f:
                data = json.load(f)
            
            for column in data.get('columns', []):
                if column.get('id') == 'in-progress':
                    tasks = column.get('tasks', [])
                    if tasks:
                        task = tasks[0]  # Get the first task
                        return f"Current task: {task.get('title')} ({task.get('progress', 0)}% complete)"
            
            return "No task currently in progress."
        except Exception as e:
            logger.error(f"Error reading Kanban board: {e}")
            return "Error reading current task information."

    def send_telegram_message(self, message):
        """Send a Telegram message with the update"""
        try:
            # Create a temporary file with the message
            msg_file = os.path.join(self.base_path, 'temp_message.txt')
            with open(msg_file, 'w') as f:
                f.write(message)
            
            # Use the message tool to send the message
            subprocess.run([
                "cat", msg_file, "|", 
                "/opt/homebrew/bin/openclaw", "message", "send", 
                "-t", "535786496", "--channel", "telegram"
            ], shell=True)
            
            # Clean up
            os.remove(msg_file)
            
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

# Create startup script
def create_startup_script():
    script_path = '/Users/karst/.openclaw/workspace/start-kanban-scheduler.sh'
    with open(script_path, 'w') as f:
        f.write('''#!/bin/bash
cd /Users/karst/.openclaw/workspace
nohup python3 kanban-scheduler.py > /dev/null 2>&1 &
echo $! > kanban-scheduler.pid
echo "Kanban scheduler started with PID $(cat kanban-scheduler.pid)"
''')
    
    os.chmod(script_path, 0o755)
    print(f"Created startup script: {script_path}")

# Run as a standalone script
if __name__ == "__main__":
    # Create startup script
    create_startup_script()
    
    # Create logs directory if it doesn't exist
    os.makedirs('/Users/karst/.openclaw/workspace/logs', exist_ok=True)
    
    scheduler = KanbanScheduler()
    
    # Run in a separate thread so this script can exit while the scheduler runs
    scheduler_thread = threading.Thread(target=scheduler.run_forever)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print("Kanban scheduler is running. Press Ctrl+C to stop.")
    
    try:
        # Just keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping scheduler...")
        scheduler.stop()
        scheduler_thread.join(timeout=5)
        print("Scheduler stopped.")