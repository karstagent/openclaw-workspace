#!/usr/bin/env python3
"""
Task Loader - Imports tasks from JSON definition files
Updates task dependencies and schedules tasks appropriately
"""

import os
import sys
import json
import logging
import importlib.util
from pathlib import Path

# Setup constants
WORKSPACE = Path("/Users/karst/.openclaw/workspace")
AUTONOMOUS_DIR = WORKSPACE / "autonomous"
LOGS_DIR = AUTONOMOUS_DIR / "logs"
TASK_DEFS_DIR = AUTONOMOUS_DIR / "task_definitions"
DASHBOARD_TASKS = AUTONOMOUS_DIR / "dashboard_tasks.json"
CUSTOM_TASKS = AUTONOMOUS_DIR / "custom_tasks.json"

# Ensure the task definitions directory exists
TASK_DEFS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "task_loader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TaskLoader")

# Import the TaskManager from task_manager.py
def import_task_manager():
    try:
        # Dynamically import the TaskManager class
        spec = importlib.util.spec_from_file_location("task_manager", AUTONOMOUS_DIR / "task_manager.py")
        task_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_manager_module)
        
        # Return the TaskManager class
        return task_manager_module.TaskManager
    except Exception as e:
        logger.error(f"Error importing TaskManager: {e}")
        return None

def load_tasks_from_file(file_path):
    """Load tasks from a JSON file"""
    if not file_path.exists():
        logger.warning(f"Task file {file_path} does not exist")
        return []
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, dict) and "tasks" in data:
            return data["tasks"]
        else:
            logger.warning(f"Invalid task file format: {file_path}")
            return []
            
    except Exception as e:
        logger.error(f"Error loading tasks from {file_path}: {e}")
        return []

def load_all_task_files():
    """Load all task definition files"""
    tasks = []
    
    # Load the main dashboard tasks
    dashboard_tasks = load_tasks_from_file(DASHBOARD_TASKS)
    if dashboard_tasks:
        tasks.extend(dashboard_tasks)
        logger.info(f"Loaded {len(dashboard_tasks)} dashboard tasks")
        
    # Load custom tasks if they exist
    custom_tasks = load_tasks_from_file(CUSTOM_TASKS)
    if custom_tasks:
        tasks.extend(custom_tasks)
        logger.info(f"Loaded {len(custom_tasks)} custom tasks")
        
    # Load any additional task files from the task_definitions directory
    for task_file in TASK_DEFS_DIR.glob("*.json"):
        file_tasks = load_tasks_from_file(task_file)
        if file_tasks:
            tasks.extend(file_tasks)
            logger.info(f"Loaded {len(file_tasks)} tasks from {task_file.name}")
            
    return tasks

def import_tasks_to_manager(tasks):
    """Import tasks to the task manager"""
    TaskManager = import_task_manager()
    if not TaskManager:
        logger.error("Failed to import TaskManager, cannot import tasks")
        return False
        
    try:
        # Create a task manager instance
        manager = TaskManager()
        
        # Current pending tasks
        current_tasks = manager.tasks["pending"]
        current_task_names = set(task.get("name", "") for task in current_tasks)
        
        # Track which dependencies have been added
        added_tasks = set()
        
        # First pass: add tasks without dependencies
        for task in tasks:
            # Skip if task is already pending
            if task["name"] in current_task_names:
                logger.info(f"Task already pending: {task['name']}")
                added_tasks.add(task["name"])
                continue
                
            # If it has no dependencies or all dependencies are satisfied
            if "dependencies" not in task or not task["dependencies"] or all(dep in added_tasks for dep in task["dependencies"]):
                # Add task to manager
                manager.add_task({
                    "name": task["name"],
                    "instructions": task["instructions"],
                    "priority": task.get("priority", 50),
                    "session_key": "main",
                    "prior_context": f"This task has an estimated duration of {task.get('estimated_duration_minutes', 60)} minutes."
                })
                
                added_tasks.add(task["name"])
                logger.info(f"Added task: {task['name']}")
        
        # Remaining passes: add tasks with dependencies until no more can be added
        remaining_tasks = [t for t in tasks if t["name"] not in added_tasks]
        while remaining_tasks:
            # Keep track of tasks added in this pass
            added_in_this_pass = set()
            
            for task in remaining_tasks:
                # Skip if task is already pending
                if task["name"] in current_task_names or task["name"] in added_tasks:
                    added_in_this_pass.add(task["name"])
                    continue
                    
                # Check if all dependencies have been added
                if "dependencies" not in task or not task["dependencies"] or all(dep in added_tasks for dep in task["dependencies"]):
                    # Add task to manager
                    manager.add_task({
                        "name": task["name"],
                        "instructions": task["instructions"],
                        "priority": task.get("priority", 50),
                        "session_key": "main",
                        "prior_context": f"This task has an estimated duration of {task.get('estimated_duration_minutes', 60)} minutes."
                    })
                    
                    added_in_this_pass.add(task["name"])
                    added_tasks.add(task["name"])
                    logger.info(f"Added task with dependencies: {task['name']}")
            
            # If no new tasks were added in this pass, we're stuck due to missing dependencies
            if not added_in_this_pass:
                logger.warning("Could not add some tasks due to unsatisfied dependencies")
                
                # Log the tasks that couldn't be added
                for task in remaining_tasks:
                    if task["name"] not in added_tasks:
                        missing_deps = [dep for dep in task.get("dependencies", []) if dep not in added_tasks]
                        logger.warning(f"Could not add task {task['name']} due to missing dependencies: {missing_deps}")
                
                break
                
            # Update remaining tasks
            remaining_tasks = [t for t in remaining_tasks if t["name"] not in added_tasks]
        
        logger.info(f"Task import complete: {len(added_tasks)} tasks added/updated")
        return True
        
    except Exception as e:
        logger.error(f"Error importing tasks: {e}")
        return False

def main():
    logger.info("Starting task loader...")
    
    # Load all task definitions
    tasks = load_all_task_files()
    logger.info(f"Loaded {len(tasks)} tasks total")
    
    # Import tasks to the task manager
    if not import_tasks_to_manager(tasks):
        logger.error("Failed to import tasks")
        return False
    
    logger.info("Task loading complete")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)