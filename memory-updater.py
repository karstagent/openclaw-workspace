#!/usr/bin/env python3
"""
Memory Updater
-------------
Updates the agent's MEMORY.md file with important insights from daily memories.
Maintains a curated long-term memory for the agent.
"""

import os
import sys
import re
import logging
import datetime
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser("~/.openclaw/workspace/logs/memory-updater.log"))
    ]
)
logger = logging.getLogger("memory-updater")

# Constants
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
MEMORY_MD_PATH = os.path.join(WORKSPACE_DIR, "MEMORY.md")

def backup_memory_file():
    """Create a backup of the current MEMORY.md file"""
    if os.path.exists(MEMORY_MD_PATH):
        backup_path = os.path.join(WORKSPACE_DIR, f"MEMORY.md.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        with open(MEMORY_MD_PATH, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        logger.info(f"Backed up MEMORY.md to {backup_path}")
        return True
    return False

def get_memory_sections():
    """Parse the MEMORY.md file into sections"""
    if not os.path.exists(MEMORY_MD_PATH):
        logger.warning(f"MEMORY.md not found at {MEMORY_MD_PATH}")
        return {}
    
    with open(MEMORY_MD_PATH, 'r') as f:
        content = f.read()
    
    # Split content into sections based on ## headers
    section_pattern = r'## ([^\n]+)([\s\S]+?)(?=## |$)'
    sections = {}
    
    # Find all section matches
    matches = re.findall(section_pattern, content)
    
    for section_name, section_content in matches:
        sections[section_name.strip()] = section_content.strip()
    
    # Handle the first section (before any ## headers)
    first_section_match = re.match(r'# [^\n]+([\s\S]+?)(?=## |$)', content)
    if first_section_match:
        sections['_intro'] = first_section_match.group(1).strip()
    
    return sections

def get_recent_daily_memories(days=7):
    """Get content from recent daily memory files"""
    memories = []
    
    # Get dates for the last N days
    dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, days + 1)]
    
    for date_str in dates:
        file_path = os.path.join(MEMORY_DIR, f"{date_str}.md")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                memories.append((date_str, f.read()))
    
    return memories

def extract_important_content(memories):
    """Extract important content from daily memories"""
    important_items = {
        "Decisions": [],
        "Action Items": [],
        "Projects": [],
        "Topics": []
    }
    
    for date_str, content in memories:
        # Extract decisions
        decision_section = re.search(r'## Decisions Made([\s\S]+?)(?=##|$)', content)
        if decision_section:
            decisions = re.findall(r'- (.+)', decision_section.group(1))
            for decision in decisions:
                important_items["Decisions"].append(f"- [{date_str}] {decision}")
        
        # Extract action items
        action_section = re.search(r'## Action Items([\s\S]+?)(?=##|$)', content)
        if action_section:
            actions = re.findall(r'- \[[ x]\] (.+)', action_section.group(1))
            for action in actions:
                important_items["Action Items"].append(f"- [{date_str}] {action}")
        
        # Extract potential project references
        project_matches = re.findall(r'(GlassWall|Mission Control|Command Station|OpenClaw Workforce|Context Retention System)', content, re.IGNORECASE)
        for match in project_matches:
            important_items["Projects"].append(f"- [{date_str}] Updated/discussed {match}")
        
        # Extract key topics
        topic_section = re.search(r'## Key Topics([\s\S]+?)(?=##|$)', content)
        if topic_section:
            topics = re.findall(r'- (.+)', topic_section.group(1))
            for topic in topics:
                important_items["Topics"].append(f"- [{date_str}] {topic}")
    
    # Remove duplicates while preserving order
    for key in important_items:
        unique_items = []
        for item in important_items[key]:
            if item not in unique_items:
                unique_items.append(item)
        important_items[key] = unique_items
    
    return important_items

def update_memory_file(sections, important_items):
    """Update the MEMORY.md file with important content"""
    # Make a backup first
    backup_memory_file()
    
    # Update each section with new content
    if "Current Projects" in sections and important_items["Projects"]:
        # Append new project updates to the section
        projects_section = sections["Current Projects"]
        projects_section += "\n" + "\n".join(important_items["Projects"][:10])  # Limit to recent 10
        sections["Current Projects"] = projects_section
    
    if "Jordan's Preferences" in sections and important_items["Decisions"]:
        # Look for decisions related to preferences
        preference_decisions = [d for d in important_items["Decisions"] if "prefer" in d.lower() or "like" in d.lower()]
        if preference_decisions:
            preferences_section = sections["Jordan's Preferences"]
            preferences_section += "\n" + "\n".join(preference_decisions)
            sections["Jordan's Preferences"] = preferences_section
    
    # Ensure there's a Recent Activities section
    if "Recent Activities" not in sections:
        sections["Recent Activities"] = ""
    
    # Update Recent Activities
    recent_activities = ["## Recent Activities", ""]
    
    if important_items["Decisions"]:
        recent_activities.extend(["### Recent Decisions", ""])
        recent_activities.extend(important_items["Decisions"][:5])  # Top 5 recent decisions
        recent_activities.append("")
    
    if important_items["Action Items"]:
        recent_activities.extend(["### Recent Action Items", ""])
        recent_activities.extend(important_items["Action Items"][:5])  # Top 5 recent actions
        recent_activities.append("")
    
    if important_items["Topics"]:
        recent_activities.extend(["### Recent Topics", ""])
        recent_activities.extend(important_items["Topics"][:5])  # Top 5 recent topics
        recent_activities.append("")
    
    sections["Recent Activities"] = "\n".join(recent_activities)
    
    # Rebuild the MEMORY.md file
    content = []
    
    # Start with the intro if it exists
    if "_intro" in sections:
        content.append(sections["_intro"])
    
    # Add all other sections
    for section_name, section_content in sections.items():
        if section_name != "_intro":
            content.append(f"## {section_name}")
            content.append(section_content)
    
    # Write the updated content
    with open(MEMORY_MD_PATH, 'w') as f:
        f.write("\n\n".join(content))
    
    logger.info(f"Updated MEMORY.md with recent important content")
    return True

def main():
    """Main function to update MEMORY.md with recent important content"""
    parser = argparse.ArgumentParser(description="Update MEMORY.md with recent content from daily memories")
    parser.add_argument('--days', type=int, default=7, help="Number of days of history to process")
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting memory updater, processing {args.days} day(s) of history")
        
        # Get current sections
        sections = get_memory_sections()
        if not sections:
            logger.error("Failed to parse MEMORY.md into sections")
            return 1
        
        # Get recent memories
        memories = get_recent_daily_memories(args.days)
        if not memories:
            logger.warning(f"No daily memories found for the past {args.days} days")
            return 0
        
        # Extract important content
        important_items = extract_important_content(memories)
        
        # Update the memory file
        update_memory_file(sections, important_items)
        
        logger.info("✅ MEMORY.md updated successfully")
        print("✅ MEMORY.md updated successfully")
        
    except Exception as e:
        logger.error(f"Error in memory updater: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())