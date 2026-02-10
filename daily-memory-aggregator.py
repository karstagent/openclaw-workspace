#!/usr/bin/env python3
"""
Daily Memory Aggregator
----------------------
Combines hourly memory summaries into a comprehensive daily summary.
Runs at the end of each day to consolidate insights and provide overview.
"""

import os
import sys
import logging
import datetime
import re
from pathlib import Path
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser("~/.openclaw/workspace/logs/daily-memory-aggregator.log"))
    ]
)
logger = logging.getLogger("daily-memory-aggregator")

# Constants
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
HOURLY_DIR = os.path.join(MEMORY_DIR, "hourly")
DAILY_MEMORY_FILE = None  # Will be set based on date

def process_hourly_summaries(date_str=None):
    """Process hourly summaries for the specified date or yesterday if not provided"""
    if date_str is None:
        # Default to yesterday
        date = datetime.date.today() - datetime.timedelta(days=1)
        date_str = date.strftime("%Y-%m-%d")
    else:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    hourly_file = os.path.join(HOURLY_DIR, f"{date_str}.md")
    
    if not os.path.exists(hourly_file):
        logger.warning(f"No hourly summaries found for {date_str}")
        return None
    
    # Set the daily memory file path
    global DAILY_MEMORY_FILE
    DAILY_MEMORY_FILE = os.path.join(MEMORY_DIR, f"{date_str}.md")
    
    with open(hourly_file, 'r') as f:
        content = f.read()
    
    return content

def extract_sections(content):
    """Extract all topics, decisions, actions, and tools from hourly summaries"""
    if not content:
        return None
    
    # Extract hourly blocks
    hour_pattern = r'### \d{4}-\d{2}-\d{2} (\d{2}:\d{2})([\s\S]+?)(?=### \d{4}-\d{2}-\d{2}|$)'
    hour_blocks = re.findall(hour_pattern, content)
    
    all_topics = []
    all_decisions = []
    all_actions = []
    all_tools = Counter()
    hours_active = []
    
    for hour, block in hour_blocks:
        hours_active.append(hour)
        
        # Extract topics
        topic_section = re.search(r'\*\*Topics Discussed:\*\*([\s\S]+?)(?=\*\*|$)', block)
        if topic_section:
            topics = re.findall(r'→ (.+)', topic_section.group(1))
            all_topics.extend(topics)
        
        # Extract decisions
        decision_section = re.search(r'\*\*Decisions Made:\*\*([\s\S]+?)(?=\*\*|$)', block)
        if decision_section:
            decisions = re.findall(r'→ (.+)', decision_section.group(1))
            all_decisions.extend(decisions)
        
        # Extract actions
        action_section = re.search(r'\*\*Action Items:\*\*([\s\S]+?)(?=\*\*|$)', block)
        if action_section:
            actions = re.findall(r'→ (.+)', action_section.group(1))
            all_actions.extend(actions)
        
        # Extract tools
        tool_section = re.search(r'\*\*Tools Used:\*\*([\s\S]+?)(?=\*\*|$)', block)
        if tool_section and tool_section.group(1).strip():
            tools_text = tool_section.group(1).strip()
            tool_matches = re.findall(r'(\w+) \((\d+)x\)', tools_text)
            for tool, count in tool_matches:
                all_tools[tool] += int(count)
    
    return {
        "topics": list(dict.fromkeys(all_topics)),  # Remove duplicates while preserving order
        "decisions": list(dict.fromkeys(all_decisions)),
        "actions": list(dict.fromkeys(all_actions)),
        "tools": all_tools,
        "hours_active": hours_active
    }

def generate_daily_summary(date_str=None):
    """Generate a comprehensive daily summary from hourly summaries"""
    content = process_hourly_summaries(date_str)
    
    if not content:
        return None
    
    sections = extract_sections(content)
    
    if not sections:
        return None
    
    date = date_str or (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Format the daily summary
    summary_lines = [
        f"# Daily Memory: {date}",
        "",
        "## Summary",
        f"Active hours: {', '.join(sections['hours_active'])}",
        "",
    ]
    
    if sections["topics"]:
        summary_lines.extend(["## Key Topics", ""])
        for topic in sections["topics"]:
            summary_lines.append(f"- {topic}")
        summary_lines.append("")
    
    if sections["decisions"]:
        summary_lines.extend(["## Decisions Made", ""])
        for decision in sections["decisions"]:
            summary_lines.append(f"- {decision}")
        summary_lines.append("")
    
    if sections["actions"]:
        summary_lines.extend(["## Action Items", ""])
        for action in sections["actions"]:
            summary_lines.append(f"- [ ] {action}")
        summary_lines.append("")
    
    if sections["tools"]:
        summary_lines.extend(["## Tool Usage", ""])
        for tool, count in sections["tools"].most_common():
            summary_lines.append(f"- {tool}: {count}x")
        summary_lines.append("")
    
    # Add raw hourly logs at the bottom for reference
    summary_lines.extend([
        "## Hourly Logs",
        "",
        content
    ])
    
    return '\n'.join(summary_lines)

def save_daily_summary(summary):
    """Save the daily summary to the memory directory"""
    if not summary:
        return
    
    with open(DAILY_MEMORY_FILE, 'w') as f:
        f.write(summary)
    
    logger.info(f"Daily summary saved to {DAILY_MEMORY_FILE}")
    return DAILY_MEMORY_FILE

def main():
    """Main function to generate and save daily memory summary"""
    try:
        # Check if date is provided as argument
        date_str = None
        if len(sys.argv) > 1:
            date_str = sys.argv[1]
            # Validate date format
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
                return 1
        
        summary = generate_daily_summary(date_str)
        
        if summary:
            file_path = save_daily_summary(summary)
            logger.info(f"✅ Daily summary created at {file_path}")
            print(f"✅ Daily summary created at {file_path}")
        else:
            logger.warning("No daily summary generated (insufficient data)")
            print("No daily summary generated (insufficient data)")
    
    except Exception as e:
        logger.error(f"Error in daily memory aggregator: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())