#!/bin/bash

# Background Task Script

# Memory File Management
echo "Organizing daily memory files..."
find ~/.openclaw/workspace/memory -type f -mtime +30 -delete

# System Health Check
echo "Performing system health check..."
system_load=$(uptime | cut -d":" -f4)
disk_usage=$(df -h / | awk '/\// {print $5}')

echo "System Load: $system_load"
echo "Disk Usage: $disk_usage"

# Update Workspace Documentation
echo "Updating workspace documentation..."
git -C ~/.openclaw/workspace pull origin main

# Log Background Activity
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
echo "Background tasks completed at $timestamp" >> ~/.openclaw/background_task_log.txt