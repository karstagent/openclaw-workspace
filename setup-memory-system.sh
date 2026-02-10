#!/bin/bash
# Master setup script for the Memory System

echo "==== Setting up Memory System ===="
echo "This script will install all memory components and cron jobs."
echo ""

# Set up directories
echo "Creating required directories..."
mkdir -p "$HOME/.openclaw/workspace/memory"
mkdir -p "$HOME/.openclaw/workspace/memory/hourly"
mkdir -p "$HOME/.openclaw/workspace/logs"
echo "✅ Directories created"
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$HOME/.openclaw/workspace/hourly-memory-summarizer.py"
chmod +x "$HOME/.openclaw/workspace/daily-memory-aggregator.py"
chmod +x "$HOME/.openclaw/workspace/memory-updater.py"
chmod +x "$HOME/.openclaw/workspace/setup-hourly-memory-cron.sh"
chmod +x "$HOME/.openclaw/workspace/setup-daily-memory-cron.sh"
chmod +x "$HOME/.openclaw/workspace/setup-memory-updater-cron.sh"
chmod +x "$HOME/.openclaw/workspace/test-memory-summarizers.sh"
echo "✅ Scripts are now executable"
echo ""

# Set up all cron jobs
echo "Setting up hourly memory summarizer cron job..."
bash "$HOME/.openclaw/workspace/setup-hourly-memory-cron.sh"
echo ""

echo "Setting up daily memory aggregator cron job..."
bash "$HOME/.openclaw/workspace/setup-daily-memory-cron.sh"
echo ""

echo "Setting up memory updater cron job..."
bash "$HOME/.openclaw/workspace/setup-memory-updater-cron.sh"
echo ""

# Show cron jobs
echo "Installed cron jobs:"
crontab -l | grep -E "hourly-memory-summarizer|daily-memory-aggregator|memory-updater"
echo ""

# Run initial test
echo "Running initial test..."
bash "$HOME/.openclaw/workspace/test-memory-summarizers.sh"
echo ""

echo "==== Memory System Setup Complete ===="
echo ""
echo "The following components have been installed:"
echo "1. Hourly Memory Summarizer (runs every hour)"
echo "2. Daily Memory Aggregator (runs at 11:59 PM daily)"
echo "3. Memory Updater (runs at 5:00 AM daily)"
echo ""
echo "To test the system manually, run:"
echo "  bash $HOME/.openclaw/workspace/test-memory-summarizers.sh"
echo ""
echo "Memory files will be stored in:"
echo "  $HOME/.openclaw/workspace/memory/"
echo ""
echo "Log files will be stored in:"
echo "  $HOME/.openclaw/workspace/logs/"
echo ""