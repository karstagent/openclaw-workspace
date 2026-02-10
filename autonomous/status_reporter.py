#!/usr/bin/env python3
"""
Status Reporter - Generates human-readable status reports
Shows system health, task progress, and overall statistics
"""

import os
import sys
import json
import logging
import datetime
import subprocess
import importlib.util
from pathlib import Path
# Try to use tabulate if available, otherwise use a simple function
try:
    from tabulate import tabulate
except ImportError:
    def tabulate(data, headers=None, tablefmt=None):
        """Simple tabulation function when tabulate package is not available"""
        if not data:
            return "No data available"
            
        result = []
        
        # Add headers if provided
        if headers:
            result.append(" | ".join(headers))
            result.append("-" * (sum(len(h) for h in headers) + (len(headers) - 1) * 3))
            
        # Add data rows
        for row in data:
            result.append(" | ".join(str(cell) for cell in row))
            
        return "\n".join(result)

# Setup constants
WORKSPACE = Path("/Users/karst/.openclaw/workspace")
AUTONOMOUS_DIR = WORKSPACE / "autonomous"
LOGS_DIR = AUTONOMOUS_DIR / "logs"
STATUS_FILE = AUTONOMOUS_DIR / "status.json"
MONITOR_STATUS_FILE = AUTONOMOUS_DIR / "monitor_status.json"
RUNNER_STATUS_FILE = AUTONOMOUS_DIR / "runner_status.json"
TASKS_FILE = AUTONOMOUS_DIR / "tasks.json"
REPORT_FILE = AUTONOMOUS_DIR / "status_report.md"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "status_reporter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StatusReporter")

def load_file(file_path):
    """Load a JSON file safely"""
    if not file_path.exists():
        return None
        
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None

def format_time_delta(seconds):
    """Format seconds into a human-readable time delta"""
    if seconds is None:
        return "Unknown"
        
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

def get_system_status():
    """Get the overall system status"""
    monitor_status = load_file(MONITOR_STATUS_FILE)
    runner_status = load_file(RUNNER_STATUS_FILE)
    
    status = {}
    
    # Check if monitor is running
    monitor_running = False
    if monitor_status:
        # Check if the timestamp is recent (within last 10 minutes)
        try:
            timestamp = datetime.datetime.fromisoformat(monitor_status["timestamp"])
            now = datetime.datetime.now()
            if (now - timestamp).total_seconds() < 600:  # 10 minutes
                monitor_running = True
                status["monitor_uptime"] = monitor_status.get("uptime", 0)
                status["monitor_status"] = monitor_status.get("status", "unknown")
        except Exception as e:
            logger.error(f"Error parsing monitor timestamp: {e}")
    
    # Check if runner is running
    runner_running = False
    if runner_status:
        # Check if the timestamp is recent (within last 10 minutes)
        try:
            timestamp = datetime.datetime.fromisoformat(runner_status["timestamp"])
            now = datetime.datetime.now()
            if (now - timestamp).total_seconds() < 600:  # 10 minutes
                runner_running = True
                status["runner_uptime"] = runner_status.get("uptime", 0)
                status["runner_status"] = runner_status.get("status", "unknown")
        except Exception as e:
            logger.error(f"Error parsing runner timestamp: {e}")
    
    # Overall status
    if monitor_running and runner_running:
        status["overall_status"] = "healthy"
    elif monitor_running:
        status["overall_status"] = "degraded"
    else:
        status["overall_status"] = "offline"
    
    return status

def get_task_statistics():
    """Get statistics about tasks"""
    tasks = load_file(TASKS_FILE)
    if not tasks:
        return None
        
    stats = {
        "pending_tasks": len(tasks.get("pending", [])),
        "completed_tasks": len(tasks.get("completed", [])),
        "failed_tasks": len(tasks.get("failed", []))
    }
    
    # Calculate completion rate
    total_processed = stats["completed_tasks"] + stats["failed_tasks"]
    if total_processed > 0:
        stats["completion_rate"] = round((stats["completed_tasks"] / total_processed) * 100, 1)
    else:
        stats["completion_rate"] = 0
    
    # Get the next pending task
    if stats["pending_tasks"] > 0:
        pending_tasks = tasks.get("pending", [])
        if pending_tasks:
            # Sort by priority
            pending_tasks.sort(key=lambda x: -x.get("priority", 0))
            stats["next_task"] = pending_tasks[0].get("name", "Unknown")
            stats["next_task_priority"] = pending_tasks[0].get("priority", 0)
    
    return stats

def get_recent_activities():
    """Get recent system activities"""
    tasks = load_file(TASKS_FILE)
    if not tasks:
        return []
        
    activities = []
    
    # Add completed tasks
    for task in tasks.get("completed", [])[-5:]:  # Last 5 completed tasks
        try:
            completed_at = datetime.datetime.fromisoformat(task.get("completed_at", ""))
            activities.append({
                "timestamp": completed_at,
                "type": "task_completed",
                "message": f"Completed task: {task.get('name', 'Unknown')}"
            })
        except Exception:
            pass
    
    # Add failed tasks
    for task in tasks.get("failed", [])[-5:]:  # Last 5 failed tasks
        try:
            failed_at = datetime.datetime.fromisoformat(task.get("failed_at", ""))
            activities.append({
                "timestamp": failed_at,
                "type": "task_failed",
                "message": f"Failed task: {task.get('name', 'Unknown')} - {task.get('error', 'Unknown error')}"
            })
        except Exception:
            pass
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:10]  # Return the 10 most recent activities

def generate_report():
    """Generate a complete status report"""
    now = datetime.datetime.now()
    system_status = get_system_status()
    task_stats = get_task_statistics()
    activities = get_recent_activities()
    
    report = [
        f"# Autonomous System Status Report",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## System Status: {system_status.get('overall_status', 'Unknown').upper()}",
        "",
        f"- **Monitor**: {'Running' if system_status.get('monitor_uptime') else 'Stopped'}"
    ]
    
    if system_status.get('monitor_uptime'):
        report.append(f"  - Uptime: {format_time_delta(system_status['monitor_uptime'])}")
        report.append(f"  - Status: {system_status.get('monitor_status', 'unknown')}")
    
    report.append(f"- **Runner**: {'Running' if system_status.get('runner_uptime') else 'Stopped'}")
    
    if system_status.get('runner_uptime'):
        report.append(f"  - Uptime: {format_time_delta(system_status['runner_uptime'])}")
        report.append(f"  - Status: {system_status.get('runner_status', 'unknown')}")
    
    report.append("")
    report.append("## Task Statistics")
    report.append("")
    
    if task_stats:
        report.append(f"- **Pending Tasks**: {task_stats['pending_tasks']}")
        report.append(f"- **Completed Tasks**: {task_stats['completed_tasks']}")
        report.append(f"- **Failed Tasks**: {task_stats['failed_tasks']}")
        report.append(f"- **Completion Rate**: {task_stats.get('completion_rate', 0)}%")
        
        if task_stats.get('next_task'):
            report.append("")
            report.append(f"**Next Task**: {task_stats['next_task']}")
            report.append(f"**Priority**: {task_stats['next_task_priority']}")
    else:
        report.append("No task statistics available")
    
    report.append("")
    report.append("## Recent Activities")
    report.append("")
    
    if activities:
        for activity in activities:
            timestamp = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            report.append(f"- **{timestamp}**: {activity['message']}")
    else:
        report.append("No recent activities")
    
    # Add process status
    report.append("")
    report.append("## Process Status")
    report.append("")
    
    try:
        # Get processes related to the autonomous system
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        processes = []
        for line in result.stdout.splitlines()[1:]:  # Skip header
            if "python" in line and any(p in line for p in ["task_manager.py", "continuous_runner.py", "system_monitor.py"]):
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "start": parts[8],
                        "time": parts[9],
                        "command": " ".join(parts[10:])
                    })
        
        if processes:
            headers = ["PID", "CPU %", "MEM %", "Started", "Runtime", "Command"]
            table_data = []
            
            for proc in processes:
                table_data.append([
                    proc['pid'],
                    proc['cpu'],
                    proc['mem'],
                    proc['start'],
                    proc['time'],
                    proc['command'][:50] + ("..." if len(proc['command']) > 50 else "")
                ])
            
            report.append("```")
            report.append(tabulate(table_data, headers=headers, tablefmt="grid"))
            report.append("```")
        else:
            report.append("No autonomous system processes found")
    except Exception as e:
        logger.error(f"Error getting process status: {e}")
        report.append(f"Error getting process status: {e}")
    
    # Return the full report
    return "\n".join(report)

def save_report(report):
    """Save the report to a file"""
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    logger.info(f"Report saved to {REPORT_FILE}")

def main():
    logger.info("Generating status report...")
    
    try:
        # Generate the report
        report = generate_report()
        
        # Save the report to a file
        save_report(report)
        
        # Print the report to stdout
        print(report)
        
        logger.info("Status report generation complete")
        return True
    except Exception as e:
        logger.error(f"Error generating status report: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)