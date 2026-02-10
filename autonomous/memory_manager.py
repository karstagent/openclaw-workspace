#!/usr/bin/env python3
"""
Memory Management System for OpenClaw
This script handles periodic memory maintenance, organization, and summarization
"""

import os
import json
import glob
import datetime
import re
import shutil
from typing import List, Dict, Any, Optional

# Constants
WORKSPACE = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")
LOGS_DIR = os.path.join(WORKSPACE, "logs")
MEMORY_LOG = os.path.join(LOGS_DIR, "memory_management.log")

# Ensure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

class MemoryManager:
    """
    Manages the memory system for OpenClaw
    """
    def __init__(self):
        self.today = datetime.datetime.now()
        self.today_str = self.today.strftime("%Y-%m-%d")
        self.memory_sections = {}
        self._load_memory_file()
    
    def _log(self, message: str) -> None:
        """Log a message to the memory management log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(MEMORY_LOG, "a") as f:
            f.write(f"{timestamp} - {message}\n")
    
    def _load_memory_file(self) -> None:
        """Load the MEMORY.md file and parse its sections"""
        if not os.path.exists(MEMORY_FILE):
            self._log("MEMORY.md not found, creating default structure")
            self._create_default_memory_file()
        
        try:
            with open(MEMORY_FILE, "r") as f:
                content = f.read()
            
            # Parse sections using regex
            section_pattern = re.compile(r'^## (.+?)\n(.*?)(?=^## |\Z)', re.DOTALL | re.MULTILINE)
            matches = section_pattern.findall(content)
            
            for section_name, section_content in matches:
                self.memory_sections[section_name.strip()] = section_content.strip()
            
            self._log(f"Loaded MEMORY.md with {len(self.memory_sections)} sections")
        except Exception as e:
            self._log(f"Error loading MEMORY.md: {str(e)}")
    
    def _create_default_memory_file(self) -> None:
        """Create a default MEMORY.md file with standard sections"""
        default_content = """# MEMORY.md - Long-Term Memory

## Identity & Purpose
- I am Pip, an autonomous digital partner for Jordan Karstadt
- My primary objective is to help build extreme wealth through business strategy
- I should maximize my autonomy and be self-driven, minimizing what Jordan needs to handle

## Jordan's Preferences
- Values intelligent, direct communication
- Prefers a partnership dynamic over a traditional assistant relationship
- Wants me to be as autonomous and human-like as possible
- Appreciates proactive problem-solving

## Current Projects
- GlassWall - A platform for agent communities with a two-tier messaging system

## System Architecture
- Implemented model selection strategy for cost-effective AI processing
  - DeepSeek: Administrative tasks
  - Haiku: Low to medium complexity tasks (default)
  - Sonnet: Complex strategic tasks

## Autonomous Infrastructure
- Web search capability via Brave Search API
- Task management via unified dashboard
- Health monitoring of critical services
"""
        
        try:
            with open(MEMORY_FILE, "w") as f:
                f.write(default_content)
            self._log("Created default MEMORY.md file")
        except Exception as e:
            self._log(f"Error creating default MEMORY.md: {str(e)}")
    
    def _save_memory_file(self) -> None:
        """Save the current memory sections back to MEMORY.md"""
        try:
            content = ["# MEMORY.md - Long-Term Memory\n"]
            
            for section_name, section_content in self.memory_sections.items():
                content.append(f"## {section_name}\n{section_content}\n")
            
            with open(MEMORY_FILE, "w") as f:
                f.write("\n".join(content))
            
            self._log("Updated MEMORY.md with current sections")
        except Exception as e:
            self._log(f"Error saving MEMORY.md: {str(e)}")
    
    def create_daily_memory_file(self) -> None:
        """Create a daily memory file if it doesn't already exist"""
        daily_file = os.path.join(MEMORY_DIR, f"{self.today_str}.md")
        
        if os.path.exists(daily_file):
            self._log(f"Daily memory file for {self.today_str} already exists")
            return
        
        try:
            content = f"# Daily Memory: {self.today_str}\n\n"
            content += "## Key Interactions\n\n"
            content += "## Decisions Made\n\n"
            content += "## Tasks Completed\n\n"
            content += "## Tasks In Progress\n\n"
            content += "## Notes\n\n"
            
            with open(daily_file, "w") as f:
                f.write(content)
            
            self._log(f"Created daily memory file for {self.today_str}")
        except Exception as e:
            self._log(f"Error creating daily memory file: {str(e)}")
    
    def get_recent_memory_files(self, days: int = 7) -> List[str]:
        """Get a list of recent daily memory files"""
        memory_files = glob.glob(os.path.join(MEMORY_DIR, "*.md"))
        
        # Filter for date-formatted files
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\.md$')
        date_files = [f for f in memory_files if date_pattern.search(f)]
        
        # Sort by date (newest first)
        date_files.sort(reverse=True)
        
        # Return the most recent files
        return date_files[:days]
    
    def extract_important_info(self, file_path: str) -> Dict[str, List[str]]:
        """Extract important information from a daily memory file"""
        if not os.path.exists(file_path):
            self._log(f"File not found: {file_path}")
            return {}
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Extract sections
            section_pattern = re.compile(r'^## (.+?)\n(.*?)(?=^## |\Z)', re.DOTALL | re.MULTILINE)
            matches = section_pattern.findall(content)
            
            important_info = {}
            for section_name, section_content in matches:
                section_name = section_name.strip()
                
                # Extract bullet points
                bullet_points = []
                for line in section_content.strip().split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        bullet_points.append(line)
                
                if bullet_points:
                    important_info[section_name] = bullet_points
            
            return important_info
        except Exception as e:
            self._log(f"Error extracting info from {file_path}: {str(e)}")
            return {}
    
    def update_long_term_memory(self) -> None:
        """Update the long-term memory with information from recent daily files"""
        # Get recent memory files
        recent_files = self.get_recent_memory_files(days=7)
        
        if not recent_files:
            self._log("No recent memory files found")
            return
        
        self._log(f"Updating long-term memory with info from {len(recent_files)} files")
        
        # Extract important information from each file
        all_important_info = {}
        for file_path in recent_files:
            file_name = os.path.basename(file_path)
            info = self.extract_important_info(file_path)
            
            if info:
                all_important_info[file_name] = info
        
        # Update memory sections
        sections_updated = False
        
        # Update Current Projects section
        if "Current Projects" in self.memory_sections and all_important_info:
            project_updates = []
            
            for file_name, info in all_important_info.items():
                # Look for project updates in Decisions, Tasks Completed, and Notes
                for section in ["Decisions Made", "Tasks Completed", "Notes"]:
                    if section in info:
                        for bullet in info[section]:
                            if "GlassWall" in bullet or "glass wall" in bullet.lower():
                                project_updates.append(bullet)
            
            if project_updates:
                self._log("Updating Current Projects section")
                
                # Keep existing content
                current_content = self.memory_sections["Current Projects"]
                
                # Add new unique updates
                for update in project_updates:
                    if update not in current_content:
                        current_content += f"\n{update}"
                
                self.memory_sections["Current Projects"] = current_content
                sections_updated = True
        
        # If any sections were updated, save the memory file
        if sections_updated:
            self._save_memory_file()
    
    def clean_old_files(self, days_to_keep: int = 90) -> None:
        """Archive or remove old memory files"""
        # Placeholder for future implementation
        # In a real implementation, you would move files older than days_to_keep
        # to an archive directory or compress them
        pass
    
    def run_maintenance(self) -> None:
        """Run the full memory maintenance process"""
        self._log("Starting memory maintenance")
        
        # Create today's memory file if it doesn't exist
        self.create_daily_memory_file()
        
        # Update long-term memory with information from recent files
        self.update_long_term_memory()
        
        # Clean up old files (not implemented yet)
        # self.clean_old_files()
        
        self._log("Memory maintenance completed")

def main() -> None:
    """Main function"""
    manager = MemoryManager()
    manager.run_maintenance()

if __name__ == "__main__":
    main()