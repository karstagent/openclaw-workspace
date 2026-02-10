#!/usr/bin/env python3
"""
Daily Initiative Scan Script - Autonomous Task Identification System

This script automatically scans the workspace to identify areas needing attention,
stalled projects, systems lacking monitoring, documentation gaps, and efficiency 
opportunities. It generates task suggestions and metrics about autonomous behavior.

The goal is to proactively identify work that needs to be done without requiring 
explicit instructions, embodying the principle: "Don't ask if you should - tell what you did."
"""

import os
import json
import datetime
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Constants
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs")
KANBAN_BOARD_PATH = os.path.join(WORKSPACE_DIR, "kanban-board.json")
METRICS_PATH = os.path.join(WORKSPACE_DIR, "autonomous-metrics.json")
REPORT_PATH = os.path.join(WORKSPACE_DIR, "autonomous-initiative-report.md")

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "initiative-scan.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("initiative-scan")

class InitiativeScanner:
    """Scans the workspace to identify areas needing attention and tracks autonomous metrics."""
    
    def __init__(self):
        self.now = datetime.datetime.now()
        self.metrics = self._load_metrics()
        self.board_data = self._load_kanban_board()
        self.opportunities = []
        self.autonomous_tasks = []
        self.requested_tasks = []
        
    def _load_metrics(self):
        """Load existing metrics or initialize new ones."""
        if os.path.exists(METRICS_PATH):
            try:
                with open(METRICS_PATH, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {METRICS_PATH}, creating new metrics")
        
        # Default metrics structure
        return {
            "task_origin": {
                "self_initiated": 0,
                "requested": 0
            },
            "time_metrics": {
                "avg_opportunity_to_action_hours": 0,
                "avg_problem_to_solution_hours": 0
            },
            "impact_metrics": {
                "time_saved_hours": 0,
                "problems_prevented": 0,
                "system_improvements": 0
            },
            "initiative_areas": {
                "monitoring": 0,
                "documentation": 0,
                "automation": 0,
                "research": 0
            },
            "historical": []
        }
    
    def _load_kanban_board(self):
        """Load the Kanban board data."""
        if os.path.exists(KANBAN_BOARD_PATH):
            try:
                with open(KANBAN_BOARD_PATH, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {KANBAN_BOARD_PATH}")
                return {"columns": []}
        return {"columns": []}
    
    def scan_all(self):
        """Run all scanners to identify opportunities."""
        logger.info("Starting initiative scan...")
        
        self.scan_stalled_projects()
        self.scan_missing_documentation()
        self.scan_unmonitored_systems()
        self.scan_automation_opportunities()
        self.scan_task_assignments()
        self.update_task_metrics()
        
        logger.info(f"Scan complete. Found {len(self.opportunities)} opportunities.")
        return self.opportunities
    
    def scan_stalled_projects(self):
        """Identify projects that haven't been updated recently."""
        logger.info("Scanning for stalled projects...")
        
        # Example implementation - identify directories with no recent updates
        threshold_days = 3
        cutoff_time = self.now - datetime.timedelta(days=threshold_days)
        
        project_dirs = [d for d in os.listdir(WORKSPACE_DIR) 
                       if os.path.isdir(os.path.join(WORKSPACE_DIR, d)) 
                       and not d.startswith('.') 
                       and not d in ['logs', 'memory', 'venv']]
        
        for project in project_dirs:
            project_path = os.path.join(WORKSPACE_DIR, project)
            latest_mod = max([os.path.getmtime(os.path.join(root, file))
                             for root, _, files in os.walk(project_path)
                             for file in files] or [0])
            
            if latest_mod > 0 and datetime.datetime.fromtimestamp(latest_mod) < cutoff_time:
                self.opportunities.append({
                    "type": "stalled_project",
                    "name": project,
                    "path": project_path,
                    "last_modified": datetime.datetime.fromtimestamp(latest_mod).isoformat(),
                    "suggestion": f"Review and continue work on {project} project",
                    "priority": "medium"
                })
    
    def scan_missing_documentation(self):
        """Identify code files without corresponding documentation."""
        logger.info("Scanning for missing documentation...")
        
        # Example: Find Python files without docstrings
        for root, _, files in os.walk(WORKSPACE_DIR):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    
                    # Skip virtual environment files
                    if "venv" in rel_path:
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for module docstring
                    if not re.search(r'^""".*?"""', content, re.DOTALL) and not re.search(r"^'''.*?'''", content, re.DOTALL):
                        self.opportunities.append({
                            "type": "missing_documentation",
                            "name": rel_path,
                            "path": file_path,
                            "suggestion": f"Add proper docstring to {rel_path}",
                            "priority": "low"
                        })
    
    def scan_unmonitored_systems(self):
        """Identify systems without proper monitoring."""
        logger.info("Scanning for unmonitored systems...")
        
        # Example: Look for Python scripts that don't write to log files
        py_scripts = []
        for root, _, files in os.walk(WORKSPACE_DIR):
            for file in files:
                if file.endswith('.py') and os.path.getsize(os.path.join(root, file)) > 500:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    
                    # Skip virtual environment files
                    if "venv" in rel_path:
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if it's a runnable script without logging
                    if "if __name__ == '__main__'" in content and not re.search(r'logging\.', content):
                        self.opportunities.append({
                            "type": "unmonitored_system",
                            "name": rel_path,
                            "path": file_path,
                            "suggestion": f"Add proper logging to {rel_path}",
                            "priority": "medium"
                        })
    
    def scan_automation_opportunities(self):
        """Identify tasks that could be automated."""
        logger.info("Scanning for automation opportunities...")
        
        # Example: Find shell scripts that could be converted to Python
        for root, _, files in os.walk(WORKSPACE_DIR):
            for file in files:
                if file.endswith('.sh') and os.path.getsize(os.path.join(root, file)) > 300:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
                    
                    # Check if we already have a Python version
                    py_equivalent = os.path.join(root, file[:-3] + '.py')
                    if not os.path.exists(py_equivalent):
                        self.opportunities.append({
                            "type": "automation_opportunity",
                            "name": rel_path,
                            "path": file_path,
                            "suggestion": f"Convert {rel_path} to a Python script for better error handling and maintainability",
                            "priority": "low"
                        })
    
    def scan_task_assignments(self):
        """Analyze task assignments and identify imbalances."""
        logger.info("Scanning task assignments...")
        
        # Count tasks by assignee, category, and requester
        assignments = Counter()
        categories = Counter()
        requesters = Counter()
        
        for column in self.board_data.get("columns", []):
            for task in column.get("tasks", []):
                assignments[task.get("assignedTo", "Unknown")] += 1
                categories[task.get("category", "other")] += 1
                requesters[task.get("assignedBy", "Unknown")] += 1
                
                # Track autonomous vs. requested tasks
                if task.get("assignedBy") == task.get("assignedTo"):
                    self.autonomous_tasks.append(task)
                else:
                    self.requested_tasks.append(task)
        
        # Check for category gaps
        essential_categories = ["development", "research", "documentation", "maintenance"]
        for category in essential_categories:
            if categories[category] == 0:
                self.opportunities.append({
                    "type": "category_gap",
                    "name": f"No {category} tasks",
                    "suggestion": f"Create tasks in the {category} category to ensure balanced development",
                    "priority": "medium"
                })
    
    def update_task_metrics(self):
        """Update metrics based on task analysis."""
        logger.info("Updating task metrics...")
        
        # Update task origin metrics
        self.metrics["task_origin"]["self_initiated"] = len(self.autonomous_tasks)
        self.metrics["task_origin"]["requested"] = len(self.requested_tasks)
        
        # Create historical record
        today_str = self.now.strftime("%Y-%m-%d")
        self.metrics["historical"].append({
            "date": today_str,
            "self_initiated": len(self.autonomous_tasks),
            "requested": len(self.requested_tasks),
            "ratio": len(self.autonomous_tasks) / max(1, len(self.requested_tasks))
        })
        
        # Trim historical data to keep only the last 30 days
        if len(self.metrics["historical"]) > 30:
            self.metrics["historical"] = self.metrics["historical"][-30:]
        
        # Save updated metrics
        with open(METRICS_PATH, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def generate_report(self):
        """Generate a markdown report of findings and metrics."""
        logger.info("Generating initiative report...")
        
        report = f"# Daily Initiative Scan Report\n\n"
        report += f"Generated: {self.now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Metrics summary
        report += "## Initiative Metrics\n\n"
        report += f"- **Self-Initiated Tasks:** {self.metrics['task_origin']['self_initiated']}\n"
        report += f"- **Requested Tasks:** {self.metrics['task_origin']['requested']}\n"
        
        if self.metrics['task_origin']['requested'] > 0:
            ratio = self.metrics['task_origin']['self_initiated'] / self.metrics['task_origin']['requested']
            report += f"- **Autonomy Ratio:** {ratio:.2f} (target: >3.0)\n\n"
        else:
            report += f"- **Autonomy Ratio:** ∞ (all tasks self-initiated)\n\n"
        
        # Opportunities
        if self.opportunities:
            report += "## Opportunities Identified\n\n"
            
            # Group by priority
            by_priority = defaultdict(list)
            for opp in self.opportunities:
                by_priority[opp.get("priority", "medium")].append(opp)
            
            for priority in ["critical", "high", "medium", "low"]:
                if priority in by_priority:
                    report += f"### {priority.title()} Priority\n\n"
                    for opp in by_priority[priority]:
                        report += f"- **{opp['suggestion']}**\n"
                        if "name" in opp:
                            report += f"  - Item: {opp['name']}\n"
                        if "type" in opp:
                            report += f"  - Type: {opp['type']}\n"
                        report += "\n"
        else:
            report += "## No New Opportunities Identified\n\n"
            report += "All systems are currently well-maintained and up-to-date.\n\n"
        
        # Historical trend
        report += "## Autonomy Trend\n\n"
        report += "Date | Self-Initiated | Requested | Ratio\n"
        report += "---- | ------------- | --------- | -----\n"
        
        for entry in reversed(self.metrics["historical"][-7:]):  # Last 7 days
            ratio = entry["self_initiated"] / max(1, entry["requested"])
            report += f"{entry['date']} | {entry['self_initiated']} | {entry['requested']} | {ratio:.2f}\n"
        
        # Write the report
        with open(REPORT_PATH, 'w') as f:
            f.write(report)
        
        logger.info(f"Report written to {REPORT_PATH}")
        return report

def main():
    """Main entry point for the initiative scanner."""
    scanner = InitiativeScanner()
    opportunities = scanner.scan_all()
    report = scanner.generate_report()
    
    print(f"\nFound {len(opportunities)} opportunities for autonomous action")
    print(f"Report saved to {REPORT_PATH}")
    
    # Create task suggestions for the Kanban board
    print("\nTop opportunities that could be added to the Kanban board:")
    
    high_priority = [o for o in opportunities if o.get("priority") in ["critical", "high"]]
    for i, opp in enumerate(high_priority[:3], 1):
        print(f"{i}. {opp['suggestion']} ({opp.get('priority', 'medium')} priority)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())