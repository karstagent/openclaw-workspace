#!/usr/bin/env python3
"""
Hourly Memory Summarizer - Context Retention System Component 1

This script runs hourly to summarize conversations, decisions, action items,
and context into a structured daily memory file.

Features:
- Extracts conversation topics, decisions, and action items
- Generates structured summaries in markdown format
- Organizes by time blocks for easy reference
- Maintains statistics about message counts and tool usage
- Provides easy lookup for important information
"""

import os
import re
import json
import time
import glob
import argparse
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/memory-summarizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('memory-summarizer')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
SESSION_LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs", "sessions")
SUMMARY_DIR = os.path.join(MEMORY_DIR, "hourly-summaries")
DAILY_SUMMARY_PATH = os.path.join(MEMORY_DIR, "{date}.md")
MEMORY_MD_PATH = os.path.join(WORKSPACE_DIR, "MEMORY.md")

# Make sure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "logs"), exist_ok=True)

class MessageProcessor:
    """Process and analyze conversation messages to extract key information"""
    
    def __init__(self):
        self.decision_patterns = [
            r"(?i)(?:I decided|we decided|decided to|decision to|concluded to|determined to|resolved to|opted to|chose to|will) ([^\.\n]+)",
            r"(?i)The (?:decision|conclusion|determination|plan) (?:is|was) to ([^\.\n]+)",
        ]
        
        self.action_item_patterns = [
            r"(?i)(?:need to|will|should|must|going to|plan to|task:) ([^\.\n]+)",
            r"(?i)(?:Action item|TODO|To-do|Task|Next step)s?:?\s*([^\.\n]+)",
        ]
        
        self.tool_usage_pattern = r"<invoke name=\"([^\"]+)\">"
    
    def extract_decisions(self, text):
        """Extract decisions from text using patterns"""
        decisions = []
        
        for pattern in self.decision_patterns:
            matches = re.findall(pattern, text)
            decisions.extend(matches)
        
        return [d.strip() for d in decisions if len(d.strip()) > 10]
    
    def extract_action_items(self, text):
        """Extract action items from text using patterns"""
        action_items = []
        
        for pattern in self.action_item_patterns:
            matches = re.findall(pattern, text)
            action_items.extend(matches)
        
        return [a.strip() for a in action_items if len(a.strip()) > 10]
    
    def extract_tool_usage(self, text):
        """Extract tool usage from text"""
        return Counter(re.findall(self.tool_usage_pattern, text))
    
    def extract_topics(self, text, n=5):
        """Extract main topics from conversation using simple keyword frequency"""
        # Remove common words and punctuation
        stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
                         "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
                         'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 
                         'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 
                         'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 
                         'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
                         'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
                         'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
                         'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
                         'with', 'about', 'against', 'between', 'into', 'through', 'during', 
                         'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                         'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 
                         'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 
                         'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
                         'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
                         'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 
                         "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 
                         've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', 
                         "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 
                         'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 
                         'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', 
                         "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 
                         'wouldn', "wouldn't", 'function', 'results', 'tool', 'let', 'sure',
                         'get', 'make', 'use', 'need', 'want', 'see', 'try', 'look'])
                         
        # Clean text and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        word_freq = Counter(words)
        return [word for word, count in word_freq.most_common(n)]

class ConversationSummarizer:
    """Generate structured summaries from conversation data"""
    
    def __init__(self):
        self.processor = MessageProcessor()
        
    def get_session_logs(self, hours_back=1):
        """Get session logs from the last N hours"""
        cutoff_time = time.time() - (hours_back * 3600)
        log_files = glob.glob(os.path.join(SESSION_LOGS_DIR, "*.json"))
        
        recent_logs = []
        for log_file in log_files:
            file_stat = os.stat(log_file)
            if file_stat.st_mtime >= cutoff_time:
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                        if isinstance(log_data, dict) and 'messages' in log_data:
                            recent_logs.append(log_data)
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
        
        return recent_logs
    
    def process_logs(self, logs):
        """Process logs and extract summary information"""
        all_messages = []
        all_text = ""
        tool_usage = Counter()
        
        # First, extract all messages and combine text
        for log in logs:
            if 'messages' in log:
                messages = log['messages']
                all_messages.extend(messages)
                
                for msg in messages:
                    if 'content' in msg:
                        all_text += msg['content'] + "\n\n"
                        
                        # Extract tool usage from assistant messages
                        if msg.get('role') == 'assistant':
                            tool_usage.update(self.processor.extract_tool_usage(msg['content']))
        
        # Sort messages by timestamp if available
        all_messages.sort(key=lambda m: m.get('timestamp', 0))
        
        # Extract various insights
        decisions = self.processor.extract_decisions(all_text)
        action_items = self.processor.extract_action_items(all_text)
        topics = self.processor.extract_topics(all_text)
        
        # Calculate statistics
        message_count = len(all_messages)
        human_messages = sum(1 for m in all_messages if m.get('role') == 'user')
        assistant_messages = sum(1 for m in all_messages if m.get('role') == 'assistant')
        
        return {
            'messages': all_messages,
            'topics': topics,
            'decisions': decisions,
            'action_items': action_items,
            'tool_usage': dict(tool_usage),
            'stats': {
                'total_messages': message_count,
                'human_messages': human_messages,
                'assistant_messages': assistant_messages,
            }
        }
    
    def generate_hourly_summary(self, data, hour):
        """Generate markdown summary for the hour"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hour_range = f"{hour:02d}:00 - {hour:02d}:59"
        
        # Create a unique ID for this summary based on content
        content_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
        summary_id = f"summary-{datetime.now().strftime('%Y%m%d')}-{hour:02d}-{content_hash}"
        
        summary = f"# Hourly Summary: {hour_range}\n\n"
        summary += f"Generated: {timestamp}\n\n"
        summary += f"ID: {summary_id}\n\n"
        
        # Add topics if available
        if data['topics']:
            summary += "## Topics\n\n"
            summary += ", ".join(data['topics']) + "\n\n"
        
        # Add decisions if available
        if data['decisions']:
            summary += "## Decisions\n\n"
            for decision in data['decisions']:
                summary += f"- {decision}\n"
            summary += "\n"
        
        # Add action items if available
        if data['action_items']:
            summary += "## Action Items\n\n"
            for item in data['action_items']:
                summary += f"- {item}\n"
            summary += "\n"
        
        # Add tool usage statistics
        if data['tool_usage']:
            summary += "## Tool Usage\n\n"
            for tool, count in sorted(data['tool_usage'].items(), key=lambda x: x[1], reverse=True):
                summary += f"- {tool}: {count} calls\n"
            summary += "\n"
        
        # Add message statistics
        summary += "## Statistics\n\n"
        summary += f"- Total Messages: {data['stats']['total_messages']}\n"
        summary += f"- Human Messages: {data['stats']['human_messages']}\n"
        summary += f"- Assistant Messages: {data['stats']['assistant_messages']}\n\n"
        
        return summary
    
    def save_hourly_summary(self, summary, hour):
        """Save hourly summary to file"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}-{hour:02d}00.md"
        filepath = os.path.join(SUMMARY_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(summary)
        
        logger.info(f"Saved hourly summary to {filepath}")
        return filepath
    
    def update_daily_summary(self, hour_summary, hour):
        """Update or create daily summary file with hourly summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_path = DAILY_SUMMARY_PATH.format(date=today)
        
        # Create daily file if it doesn't exist
        if not os.path.exists(daily_path):
            with open(daily_path, 'w') as f:
                f.write(f"# Daily Summary: {today}\n\n")
                f.write("*This file is automatically updated by the hourly memory summarizer*\n\n")
        
        # Read existing content
        with open(daily_path, 'r') as f:
            content = f.read()
        
        # Check if hour section already exists
        hour_header = f"## {hour:02d}:00 - {hour:02d}:59"
        if hour_header in content:
            # Replace existing section
            pattern = f"{hour_header}.*?(?=^## |$)"
            replacement = hour_summary.split("# Hourly Summary:")[1].strip()
            updated_content = re.sub(pattern, f"{hour_header}\n\n{replacement}\n\n", content, flags=re.DOTALL | re.MULTILINE)
        else:
            # Add new section at the top, after the header
            header_end = content.find("\n\n") + 2
            updated_content = content[:header_end] + f"{hour_header}\n\n{hour_summary.split('# Hourly Summary:')[1].strip()}\n\n" + content[header_end:]
        
        # Write updated content
        with open(daily_path, 'w') as f:
            f.write(updated_content)
        
        logger.info(f"Updated daily summary at {daily_path}")
        return daily_path
    
    def update_memory_md(self, data):
        """Update MEMORY.md with important information from today's summaries"""
        # This is a placeholder for now - we'll implement a more sophisticated 
        # approach that periodically reviews daily summaries and extracts the
        # most important items for long-term memory
        pass
    
    def run(self, hour=None, hours_back=1):
        """Run the summarization process"""
        if hour is None:
            hour = datetime.now().hour
            
        logger.info(f"Starting summarization for hour {hour}")
        
        # Get and process logs
        logs = self.get_session_logs(hours_back)
        if not logs:
            logger.info(f"No logs found for the past {hours_back} hour(s)")
            return
            
        data = self.process_logs(logs)
        
        # Generate and save summaries
        hour_summary = self.generate_hourly_summary(data, hour)
        hourly_path = self.save_hourly_summary(hour_summary, hour)
        daily_path = self.update_daily_summary(hour_summary, hour)
        
        # Update long-term memory if needed
        self.update_memory_md(data)
        
        logger.info(f"Summarization complete. Hourly: {hourly_path}, Daily: {daily_path}")
        return {
            'hourly_path': hourly_path,
            'daily_path': daily_path,
            'stats': data['stats'],
            'topics': data['topics']
        }

def setup_cron_job():
    """Set up hourly cron job for the memory summarizer"""
    import subprocess
    
    script_path = os.path.abspath(__file__)
    cron_command = f"0 * * * * /usr/bin/python3 {script_path} --hour $(date +\\%H)"
    
    try:
        # Check if cron job already exists
        cron_check = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = cron_check.stdout if cron_check.returncode == 0 else ""
        
        if script_path in current_crontab:
            logger.info("Cron job already exists")
            return
        
        # Add new cron job
        new_crontab = current_crontab + cron_command + "\n"
        subprocess.run(['crontab', '-'], input=new_crontab, text=True)
        logger.info(f"Created hourly cron job: {cron_command}")
    except Exception as e:
        logger.error(f"Failed to set up cron job: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hourly Memory Summarizer")
    parser.add_argument("--hour", type=int, help="Hour to summarize (0-23), defaults to current hour")
    parser.add_argument("--hours-back", type=int, default=1, help="Hours to look back for logs")
    parser.add_argument("--setup-cron", action="store_true", help="Set up hourly cron job")
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron_job()
    else:
        summarizer = ConversationSummarizer()
        summarizer.run(hour=args.hour, hours_back=args.hours_back)