#!/usr/bin/env python3
"""
Post-Compaction Context Injector - Context Retention System Component 2

This script detects context window compaction events and immediately
injects recent memory summaries, messages, and thinking blocks to maintain
conversational continuity.

Features:
- Detects context window resets/compactions
- Retrieves recent memory summaries
- Injects appropriate memory content
- Maintains conversation coherence across compactions
- Configurable memory retention strategies
- Integration with OpenClaw messaging system
"""

import os
import re
import sys
import json
import time
import glob
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/context-injector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('context-injector')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
HOURLY_SUMMARIES_DIR = os.path.join(MEMORY_DIR, "hourly-summaries")
SESSION_LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs", "sessions")
CONTEXT_STATE_FILE = os.path.join(WORKSPACE_DIR, "context-state.json")
MEMORY_FILE = os.path.join(WORKSPACE_DIR, "MEMORY.md")
OPENCLAW_SCRIPT = "openclaw"  # Path to openclaw CLI

# Make sure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "logs"), exist_ok=True)
os.makedirs(HOURLY_SUMMARIES_DIR, exist_ok=True)

class ContextStateManager:
    """Manages context state tracking for detecting compaction events"""
    
    def __init__(self, state_file=CONTEXT_STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self):
        """Load state from file or create default state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading state file: {e}")
                return self._create_default_state()
        else:
            return self._create_default_state()
    
    def _create_default_state(self):
        """Create default state structure"""
        return {
            "sessions": {},
            "last_compaction_time": None,
            "last_update": datetime.now().isoformat(),
            "message_hashes": [],
            "injections": []
        }
    
    def save_state(self):
        """Save current state to file"""
        try:
            self.state["last_update"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.debug(f"State saved to {self.state_file}")
        except IOError as e:
            logger.error(f"Error saving state file: {e}")
    
    def register_message(self, session_id, message_id, content, role, timestamp=None):
        """Register a message for tracking"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Initialize session if it doesn't exist
        if session_id not in self.state["sessions"]:
            self.state["sessions"][session_id] = {
                "last_message_id": None,
                "message_count": 0,
                "messages": [],
                "last_activity": timestamp,
                "compactions": []
            }
        
        # Create message hash for duplicate detection
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check if this is a duplicate message (can happen during reconnects)
        if content_hash in self.state["message_hashes"]:
            logger.debug(f"Duplicate message detected, skipping: {message_id}")
            return False
        
        # Add message to tracking
        self.state["sessions"][session_id]["messages"].append({
            "id": message_id,
            "timestamp": timestamp,
            "role": role,
            "hash": content_hash
        })
        
        # Keep only the last 50 messages per session
        if len(self.state["sessions"][session_id]["messages"]) > 50:
            self.state["sessions"][session_id]["messages"].pop(0)
        
        # Update session state
        self.state["sessions"][session_id]["last_message_id"] = message_id
        self.state["sessions"][session_id]["message_count"] += 1
        self.state["sessions"][session_id]["last_activity"] = timestamp
        
        # Update global message hashes list (keep last 100)
        self.state["message_hashes"].append(content_hash)
        if len(self.state["message_hashes"]) > 100:
            self.state["message_hashes"].pop(0)
        
        self.save_state()
        return True
    
    def detect_compaction(self, session_id, message_id, content, role):
        """
        Detect if a context compaction has occurred
        
        Compaction detection strategies:
        1. Message ID sequence breaks
        2. Repeated system messages
        3. Explicit reset markers
        4. Context window overflow errors
        5. Memory reference failures
        """
        if session_id not in self.state["sessions"]:
            # New session, not a compaction
            return False
        
        session_state = self.state["sessions"][session_id]
        
        # Strategy 1: Check for reset markers in content
        reset_markers = [
            "I'll start fresh",
            "Let me start over",
            "I'll reset and try again",
            "Starting a new session",
            "Context has been cleared",
            "/new command detected",
            "Previous context has been reset",
            "input length and max_tokens exceed context limit",
            "context window is full",
            "context limit",
            "exceed context limit",
            "I don't have access to that information",
            "I don't have that context",
            "I don't have memory of that",
            "I cannot access previous",
            "seems I've lost some context"
        ]
        
        for marker in reset_markers:
            if marker.lower() in content.lower():
                logger.info(f"Compaction detected in session {session_id} via reset marker: '{marker}'")
                self._register_compaction(session_id)
                return True
        
        # Strategy 2: Check for repeated system messages at beginning of conversations
        if role == "system" and session_state["message_count"] > 10:
            # Look for similar system messages in recent history
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            for msg in session_state["messages"][:5]:  # Check first 5 messages
                if msg.get("hash") == content_hash:
                    logger.info(f"Compaction detected in session {session_id} via repeated system message")
                    self._register_compaction(session_id)
                    return True
        
        # Strategy 3: Context window error patterns
        error_patterns = [
            r"input length .* exceed context limit",
            r"context (?:window|limit) .* exceed",
            r"token limit exceed",
            r"context .* full",
            r"retry with (?:smaller|less) (?:context|input)"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.info(f"Compaction detected in session {session_id} via error pattern: '{pattern}'")
                self._register_compaction(session_id)
                return True
        
        return False
    
    def _register_compaction(self, session_id):
        """Register a compaction event"""
        if session_id in self.state["sessions"]:
            compaction_time = datetime.now().isoformat()
            self.state["sessions"][session_id]["compactions"].append({
                "timestamp": compaction_time,
                "message_count_before": self.state["sessions"][session_id]["message_count"]
            })
            self.state["last_compaction_time"] = compaction_time
            self.save_state()
    
    def register_injection(self, session_id, injection_content, trigger_event="compaction"):
        """Register a context injection event"""
        injection_id = f"inj_{int(time.time())}"
        
        if "injections" not in self.state:
            self.state["injections"] = []
        
        # Create a hash of the injected content
        content_hash = hashlib.md5(injection_content.encode()).hexdigest()
        
        # Register the injection
        self.state["injections"].append({
            "id": injection_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger_event,
            "content_hash": content_hash,
            "content_length": len(injection_content)
        })
        
        # Keep only the last 50 injections
        if len(self.state["injections"]) > 50:
            self.state["injections"].pop(0)
        
        self.save_state()
        return injection_id

class MemoryRetriever:
    """Retrieves relevant memory content for injection after compaction"""
    
    def __init__(self, memory_dir=MEMORY_DIR, summaries_dir=HOURLY_SUMMARIES_DIR):
        self.memory_dir = memory_dir
        self.summaries_dir = summaries_dir
    
    def get_recent_summaries(self, hours_back=24):
        """Get summaries from the last N hours"""
        summaries = []
        now = datetime.now()
        cutoff_time = now - timedelta(hours=hours_back)
        
        # List all summary files
        summary_files = glob.glob(os.path.join(self.summaries_dir, "*.md"))
        
        for file_path in sorted(summary_files, reverse=True):
            try:
                # Extract date from filename (format: YYYY-MM-DD-HHMM.md)
                filename = os.path.basename(file_path)
                if not re.match(r'\d{4}-\d{2}-\d{2}-\d{4}\.md', filename):
                    continue
                
                # Parse the timestamp from filename
                date_str, time_str = filename.replace('.md', '').rsplit('-', 1)
                hour = int(time_str[:2])
                minute = int(time_str[2:])
                
                file_date = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")
                
                # Skip if older than cutoff
                if file_date < cutoff_time:
                    continue
                
                # Read summary content
                with open(file_path, 'r') as f:
                    content = f.read()
                
                summaries.append({
                    "date": file_date.strftime("%Y-%m-%d"),
                    "time": f"{hour:02d}:{minute:02d}",
                    "content": content,
                    "path": file_path
                })
                
                # Limit to most recent 24 summaries
                if len(summaries) >= 24:
                    break
                    
            except Exception as e:
                logger.error(f"Error processing summary file {file_path}: {e}")
        
        return summaries
    
    def get_daily_memory(self, days_back=2):
        """Get recent daily memory files"""
        daily_memories = []
        now = datetime.now()
        
        for i in range(days_back):
            date = now - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            file_path = os.path.join(self.memory_dir, f"{date_str}.md")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    daily_memories.append({
                        "date": date_str,
                        "content": content,
                        "path": file_path
                    })
                except Exception as e:
                    logger.error(f"Error reading daily memory file {file_path}: {e}")
        
        return daily_memories
    
    def get_main_memory_content(self):
        """Get content from the main MEMORY.md file"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    content = f.read()
                return content
            except Exception as e:
                logger.error(f"Error reading main memory file {MEMORY_FILE}: {e}")
                return ""
        return ""
    
    def get_recent_messages(self, session_id, limit=10):
        """Get recent messages from a session"""
        try:
            # Use openclaw sessions_history to get session messages
            cmd = [
                OPENCLAW_SCRIPT, 
                "sessions_history", 
                f"sessionKey={session_id}", 
                f"limit={limit}"
            ]
            
            process = subprocess.run(
                cmd, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0 and process.stdout:
                try:
                    messages = json.loads(process.stdout)
                    return messages
                except json.JSONDecodeError:
                    # Not valid JSON, might be a formatted output
                    return [{"content": process.stdout, "role": "unknown"}]
            else:
                logger.warning(f"Failed to get session history: {process.stderr}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving recent messages: {e}")
            return []
    
    def get_task_context(self):
        """Get current task information from kanban board"""
        try:
            task_status_path = os.path.join(WORKSPACE_DIR, "current-task-status.json")
            kanban_board_path = os.path.join(WORKSPACE_DIR, "kanban-board.json")
            
            current_task = {"status": "No task in progress"}
            
            # First try to get from task status file
            if os.path.exists(task_status_path):
                try:
                    with open(task_status_path, 'r') as f:
                        task_data = json.load(f)
                        if "currentTaskStatus" in task_data:
                            current_task["status"] = task_data["currentTaskStatus"]
                except Exception:
                    pass
            
            # Also try to get more details from kanban board
            if os.path.exists(kanban_board_path):
                try:
                    with open(kanban_board_path, 'r') as f:
                        board = json.load(f)
                        
                    # Look for tasks in the in-progress column
                    for column in board.get("columns", []):
                        if column.get("id") == "in-progress":
                            for task in column.get("tasks", []):
                                return {
                                    "status": current_task["status"],
                                    "title": task.get("title", "Unknown"),
                                    "description": task.get("description", ""),
                                    "priority": task.get("priority", "medium"),
                                    "progress": task.get("progress", 0)
                                }
                except Exception as e:
                    logger.error(f"Error reading kanban board: {e}")
            
            return current_task
        except Exception as e:
            logger.error(f"Error retrieving task context: {e}")
            return {"status": "Unknown"}
    
    def generate_context_injection(self, session_id, detected_compaction=False, max_tokens=2000):
        """Generate content to be injected into the context after compaction"""
        injection = "# Context Continuity\n\n"
        
        # Add timestamp and marker
        injection += f"*Memory injection at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Token budget tracking (rough estimate)
        token_budget = max_tokens
        token_budget -= len(injection) // 4  # Very rough token estimate
        
        # Add information about the compaction event
        if detected_compaction:
            compaction_note = "## Continuity Note\n\n"
            compaction_note += "The conversation context was reset or compacted. "
            compaction_note += "This summary has been injected to maintain continuity.\n\n"
            injection += compaction_note
            token_budget -= len(compaction_note) // 4
        
        # Add current task information (highest priority)
        task_context = self.get_task_context()
        if task_context and "title" in task_context:
            task_info = f"## Current Task\n\n"
            task_info += f"**{task_context.get('title')}** "
            task_info += f"({task_context.get('progress', 0)}% complete)\n\n"
            
            if task_context.get('description'):
                description = task_context['description']
                # Truncate if too long
                if len(description) > 300:
                    description = description[:300] + "..."
                task_info += f"{description}\n\n"
            
            injection += task_info
            token_budget -= len(task_info) // 4
        
        # If not enough budget, return what we have
        if token_budget < 400:  # Minimum viable size for remaining sections
            return injection
        
        # Extract key information from MEMORY.md
        memory_content = self.get_main_memory_content()
        if memory_content:
            memory_section = "## Long-Term Memory\n\n"
            
            # Extract key sections from MEMORY.md
            important_sections = [
                "Current Projects",
                "Identity & Purpose",
                "System Architecture"
            ]
            
            for section in important_sections:
                pattern = rf"## {section}.*?\n(.*?)(?=^##|\Z)"
                match = re.search(pattern, memory_content, re.DOTALL | re.MULTILINE)
                if match:
                    content = match.group(1).strip()
                    
                    # Limit length
                    if len(content) > 500:
                        content = content[:500] + "...\n"
                    
                    memory_section += f"### {section}\n{content}\n\n"
            
            # Check if we have budget for this section
            if token_budget >= len(memory_section) // 4:
                injection += memory_section
                token_budget -= len(memory_section) // 4
            
            # If not enough budget, return what we have
            if token_budget < 400:
                return injection
        
        # Get daily memory files (lower priority)
        daily_memories = self.get_daily_memory(days_back=2)
        if daily_memories:
            today = daily_memories[0]
            today_section = f"## Today's Context ({today['date']})\n\n"
            
            # Extract just the important parts (first 400 chars)
            content_excerpt = today['content'][:400].strip()
            if len(today['content']) > 400:
                content_excerpt += "...\n\n"
            
            today_section += content_excerpt + "\n\n"
            
            # Add if within budget
            if token_budget >= len(today_section) // 4:
                injection += today_section
                token_budget -= len(today_section) // 4
        
        # Get recent summaries (lowest priority)
        summaries = self.get_recent_summaries(hours_back=24)
        if summaries and token_budget > 300:
            most_recent = summaries[0]
            summary_section = f"## Recent Activity ({most_recent['date']} {most_recent['time']})\n\n"
            
            # Extract just the most relevant parts
            summary_content = most_recent['content']
            
            # Try to extract just decisions and action items
            decisions_match = re.search(r'## Decisions\s+(.+?)(?=##|\Z)', summary_content, re.DOTALL)
            actions_match = re.search(r'## Action Items\s+(.+?)(?=##|\Z)', summary_content, re.DOTALL)
            
            if decisions_match and token_budget > 150:
                decisions_text = "### Key Decisions\n" + decisions_match.group(1).strip() + "\n\n"
                if len(decisions_text) > 300:
                    decisions_text = decisions_text[:300] + "...\n\n"
                summary_section += decisions_text
                token_budget -= len(decisions_text) // 4
            
            if actions_match and token_budget > 150:
                actions_text = "### Action Items\n" + actions_match.group(1).strip() + "\n\n"
                if len(actions_text) > 300:
                    actions_text = actions_text[:300] + "...\n\n"
                summary_section += actions_text
                token_budget -= len(actions_text) // 4
            
            # Add if content was extracted
            if len(summary_section) > 60:  # More than just the header
                injection += summary_section
        
        return injection

class MessagingManager:
    """Handles sending messages to sessions"""
    
    def inject_context(self, session_id, content):
        """Inject context into a session"""
        try:
            # Use openclaw sessions_send to inject content
            cmd = [
                OPENCLAW_SCRIPT, 
                "sessions_send", 
                f"sessionKey={session_id}", 
                f"message={content}"
            ]
            
            process = subprocess.run(
                cmd, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info(f"Successfully injected context into session {session_id}")
                return True
            else:
                logger.error(f"Failed to inject context: {process.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error injecting context: {e}")
            return False

class CompactionHandler:
    """Handles the compaction detection and response process"""
    
    def __init__(self):
        self.state_manager = ContextStateManager()
        self.memory_retriever = MemoryRetriever()
        self.messaging = MessagingManager()
    
    def process_message(self, session_id, message_id, content, role, timestamp=None):
        """Process a new message, detect compaction and inject if needed"""
        # Register the message
        is_new = self.state_manager.register_message(session_id, message_id, content, role, timestamp)
        
        if not is_new:
            # Skip duplicate messages
            return None
        
        # Check for compaction
        compaction_detected = self.state_manager.detect_compaction(session_id, message_id, content, role)
        
        if compaction_detected:
            logger.info(f"Compaction detected in session {session_id}, generating injection")
            # Generate memory injection
            injection = self.memory_retriever.generate_context_injection(
                session_id,
                detected_compaction=True
            )
            
            # Register the injection
            injection_id = self.state_manager.register_injection(
                session_id, 
                injection,
                trigger_event="compaction"
            )
            
            # Inject into session
            success = self.messaging.inject_context(session_id, injection)
            
            if success:
                logger.info(f"Successfully injected context {injection_id} into session {session_id}")
            else:
                logger.error(f"Failed to inject context {injection_id} into session {session_id}")
            
            return injection
        
        return None
    
    def monitor_logs(self):
        """Monitor session logs for compaction events"""
        # This would be implemented for a background monitoring process
        # that continually scans logs for signs of compaction
        pass
    
    def setup_cron_watcher(self):
        """Set up a cron job to regularly check for compaction events"""
        try:
            cron_cmd = [
                OPENCLAW_SCRIPT,
                "cron",
                "action=add",
                json.dumps({
                    "name": "context-compaction-watcher",
                    "schedule": {
                        "kind": "every",
                        "everyMs": 60000  # Every minute
                    },
                    "payload": {
                        "kind": "systemEvent",
                        "text": "Check for context compaction events"
                    },
                    "sessionTarget": "main",
                    "enabled": True
                })
            ]
            
            process = subprocess.run(
                cron_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info("Successfully set up compaction watcher cron job")
                return True
            else:
                logger.error(f"Failed to set up cron job: {process.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error setting up cron watcher: {e}")
            return False

def test_injection(session_id=None, token_limit=2000):
    """Run a test injection"""
    if not session_id:
        session_id = f"test-session-{int(time.time())}"
    
    retriever = MemoryRetriever()
    injection = retriever.generate_context_injection(
        session_id,
        detected_compaction=True,
        max_tokens=token_limit
    )
    
    print("\n=== Context Injection Content ===\n")
    print(injection)
    
    # Calculate approximate token count
    approx_tokens = len(injection) // 4
    print(f"\nApproximate token count: {approx_tokens}")
    
    return injection

def install_autocorrect():
    """Set up the auto-correction mechanism for context compactions"""
    try:
        # Create directory for scripts if it doesn't exist
        scripts_dir = os.path.join(WORKSPACE_DIR, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Create the handler script
        handler_path = os.path.join(scripts_dir, "compaction_handler.py")
        
        handler_content = '''#!/usr/bin/env python3
import sys
import os
import re
import logging
import json
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/compaction-handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('compaction-handler')

def handle_message(message):
    """Check if message indicates context compaction and run injector if needed"""
    compaction_indicators = [
        "input length .* exceed context limit",
        "context (?:window|limit) .* exceed",
        "token limit exceed",
        "context .* full",
        "I don't have access to that information",
        "I don't have that context",
        "I don't have memory of that"
    ]
    
    # Extract session info
    session_match = re.search(r"session[_\\s]*(?:id|key)[:\\s]*([\\w-]+)", message, re.IGNORECASE)
    session_id = session_match.group(1) if session_match else None
    
    if not session_id:
        # Try to get from environment
        session_id = os.environ.get("OPENCLAW_SESSION_ID")
    
    if not session_id:
        logger.error("Could not determine session ID")
        return
    
    # Check for compaction indicators
    for pattern in compaction_indicators:
        if re.search(pattern, message, re.IGNORECASE):
            logger.info(f"Compaction indicator detected: {pattern}")
            
            # Run the injector
            try:
                subprocess.run(
                    ["/Users/karst/.openclaw/workspace/post-compaction-inject.py", "--session", session_id, "--inject-now"],
                    check=True
                )
                logger.info(f"Ran context injector for session {session_id}")
                return
            except Exception as e:
                logger.error(f"Failed to run context injector: {e}")
                return
    
    logger.debug("No compaction indicators detected")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
        handle_message(message)
    else:
        # Read from stdin
        message = sys.stdin.read()
        handle_message(message)
'''
        with open(handler_path, 'w') as f:
            f.write(handler_content)
        
        # Make executable
        os.chmod(handler_path, 0o755)
        
        # Create the cron job
        cron_cmd = [
            OPENCLAW_SCRIPT,
            "cron",
            "action=add",
            "job=" + json.dumps({
                "name": "compaction-autocorrect",
                "schedule": {
                    "kind": "every",
                    "everyMs": 30000  # Every 30 seconds
                },
                "payload": {
                    "kind": "systemEvent",
                    "text": "Check for context compaction issues and fix automatically"
                },
                "sessionTarget": "main",
                "enabled": True
            })
        ]
        
        process = subprocess.run(
            cron_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info("Successfully set up compaction autocorrect cron job")
            print("Autocorrect mechanism installed successfully")
            return True
        else:
            logger.error(f"Failed to set up autocorrect cron job: {process.stderr}")
            print("Failed to set up autocorrect cron job")
            return False
        
    except Exception as e:
        logger.error(f"Error installing autocorrect: {e}")
        print(f"Error installing autocorrect: {e}")
        return False

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Post-Compaction Context Injector")
    parser.add_argument("--session", type=str, help="Session ID to monitor")
    parser.add_argument("--simulate", action="store_true", help="Simulate a compaction event")
    parser.add_argument("--test", action="store_true", help="Test injection content generation")
    parser.add_argument("--install-autocorrect", action="store_true", help="Install automatic correction mechanism")
    parser.add_argument("--inject-now", action="store_true", help="Force an injection now")
    parser.add_argument("--tokens", type=int, default=2000, help="Token limit for injection")
    
    args = parser.parse_args()
    
    handler = CompactionHandler()
    
    if args.install_autocorrect:
        install_autocorrect()
        return
    
    if args.test:
        test_injection(args.session, args.tokens)
        return
    
    if args.simulate:
        logger.info("Simulating a compaction event")
        session_id = args.session or f"test-session-{int(time.time())}"
        
        # Register some test messages
        for i in range(5):
            handler.process_message(
                session_id=session_id,
                message_id=f"msg_{i}",
                content=f"Test message {i}",
                role="user" if i % 2 == 0 else "assistant",
                timestamp=datetime.now().isoformat()
            )
        
        # Simulate compaction
        injection = handler.memory_retriever.generate_context_injection(
            session_id,
            detected_compaction=True,
            max_tokens=args.tokens
        )
        
        print("\n=== Context Injection Content ===\n")
        print(injection)
        
        # Calculate approximate token count
        approx_tokens = len(injection) // 4
        print(f"\nApproximate token count: {approx_tokens}")
    
    elif args.inject_now and args.session:
        logger.info(f"Forcing injection for session: {args.session}")
        
        # Generate and inject context
        injection = handler.memory_retriever.generate_context_injection(
            args.session,
            detected_compaction=True,
            max_tokens=args.tokens
        )
        
        # Register the injection
        injection_id = handler.state_manager.register_injection(
            args.session,
            injection,
            trigger_event="manual"
        )
        
        # Inject into session
        success = handler.messaging.inject_context(args.session, injection)
        
        if success:
            print(f"Successfully injected context into session {args.session}")
        else:
            print(f"Failed to inject context into session {args.session}")
    
    elif args.session:
        logger.info(f"Setting up monitoring for session: {args.session}")
        
        # Create a handler for this session
        print(f"Monitoring session {args.session} for compaction events.")
        handler.setup_cron_watcher()
        
        # Initial simulated message to register the session
        handler.process_message(
            session_id=args.session,
            message_id="initial_monitor",
            content="Starting context compaction monitoring",
            role="system",
            timestamp=datetime.now().isoformat()
        )
        
        print("Monitoring system initialized.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()