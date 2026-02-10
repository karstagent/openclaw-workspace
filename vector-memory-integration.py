#!/usr/bin/env python3
"""
Integration script for the Vector Memory Pipeline with OpenClaw.

This script provides OpenClaw command integration for the vector memory system,
allowing for easy memory search, indexing, and maintenance from within the OpenClaw environment.

Usage:
    - memory_search: Search the vector memory for relevant content
    - memory_index: Update the vector memory index with new content
    - memory_stats: View statistics about the vector memory index
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/vector-memory-integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('vector-memory-integration')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
VECTOR_MEMORY_SCRIPT = os.path.join(WORKSPACE_DIR, "vector-memory.py")
OPENCLAW_BIN = "openclaw"

def run_vector_memory_command(args):
    """Run a command with the vector memory script"""
    cmd = [sys.executable, VECTOR_MEMORY_SCRIPT] + args
    
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return f"Error: {e.stderr}"

def memory_search(query, results=5, threshold=0.5):
    """
    Search the vector memory for relevant content
    
    Args:
        query: Search query
        results: Number of results to return (default: 5)
        threshold: Minimum similarity threshold (default: 0.5)
    
    Returns:
        Search results as formatted text
    """
    args = [
        "--search", query,
        "--results", str(results),
        "--threshold", str(threshold)
    ]
    
    return run_vector_memory_command(args)

def memory_index(days_back_memory=30, days_back_sessions=7):
    """
    Update the vector memory index with recent content
    
    Args:
        days_back_memory: Days of memory files to index (default: 30)
        days_back_sessions: Days of session logs to index (default: 7)
    
    Returns:
        Indexing results as formatted text
    """
    args = [
        "--index",
        "--memory-days", str(days_back_memory),
        "--session-days", str(days_back_sessions)
    ]
    
    return run_vector_memory_command(args)

def memory_stats():
    """
    Get statistics about the vector memory index
    
    Returns:
        Statistics as formatted text
    """
    args = ["--stats"]
    return run_vector_memory_command(args)

def memory_add_file(file_path):
    """
    Add a specific file to the vector memory index
    
    Args:
        file_path: Path to the file to add
    
    Returns:
        Result as formatted text
    """
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"
    
    args = ["--add", file_path]
    return run_vector_memory_command(args)

def setup_cron_job():
    """
    Set up a daily cron job for index maintenance
    
    Returns:
        Result as formatted text
    """
    args = ["--setup-cron"]
    return run_vector_memory_command(args)

def setup_openclaw_commands():
    """
    Register the vector memory commands with OpenClaw
    
    This enables the following OpenClaw commands:
    - memory_search: Search vector memory
    - memory_index: Update vector memory index
    - memory_stats: View vector memory statistics
    """
    integration_script = os.path.abspath(__file__)
    
    # Define the commands to register
    commands = [
        {
            "name": "memory_search",
            "script": integration_script,
            "args": ["search", "${query}", "${results=5}", "${threshold=0.5}"],
            "description": "Search vector memory for semantic matches to your query"
        },
        {
            "name": "memory_index",
            "script": integration_script,
            "args": ["index", "${days_memory=30}", "${days_sessions=7}"],
            "description": "Update the vector memory index with recent conversations and files"
        },
        {
            "name": "memory_stats",
            "script": integration_script,
            "args": ["stats"],
            "description": "View statistics about the vector memory index"
        }
    ]
    
    # Register each command with OpenClaw
    for cmd in commands:
        try:
            # Prepare the command definition
            cmd_json = json.dumps(cmd)
            
            # Run openclaw command to register
            openclaw_cmd = [
                OPENCLAW_BIN,
                "command",
                "register",
                cmd_json
            ]
            
            subprocess.run(openclaw_cmd, capture_output=True, text=True, check=True)
            logger.info(f"Registered OpenClaw command: {cmd['name']}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to register command {cmd['name']}: {e}")
            logger.error(f"Error output: {e.stderr}")

def main():
    """Main entry point for CLI usage"""
    parser = argparse.ArgumentParser(description="Vector Memory OpenClaw Integration")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search vector memory")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("results", nargs="?", type=int, default=5, help="Number of results")
    search_parser.add_argument("threshold", nargs="?", type=float, default=0.5, help="Similarity threshold")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Update vector memory index")
    index_parser.add_argument("days_memory", nargs="?", type=int, default=30, help="Days of memory to index")
    index_parser.add_argument("days_sessions", nargs="?", type=int, default=7, help="Days of sessions to index")
    
    # Stats command
    subparsers.add_parser("stats", help="View vector memory statistics")
    
    # Add file command
    add_parser = subparsers.add_parser("add", help="Add a file to vector memory")
    add_parser.add_argument("file_path", help="Path to the file to add")
    
    # Setup command
    subparsers.add_parser("setup", help="Set up OpenClaw integration")
    
    args = parser.parse_args()
    
    if args.command == "search":
        print(memory_search(args.query, args.results, args.threshold))
    elif args.command == "index":
        print(memory_index(args.days_memory, args.days_sessions))
    elif args.command == "stats":
        print(memory_stats())
    elif args.command == "add":
        print(memory_add_file(args.file_path))
    elif args.command == "setup":
        setup_openclaw_commands()
        print("OpenClaw command integration complete")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()