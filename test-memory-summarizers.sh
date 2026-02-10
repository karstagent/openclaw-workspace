#!/bin/bash
# Test script for memory summarizers

echo "=== Testing Hourly Memory Summarizer ==="
python3 "$HOME/.openclaw/workspace/hourly-memory-summarizer.py"
echo ""

echo "=== Testing Daily Memory Aggregator ==="
# Use today's date for testing
TODAY=$(date +%Y-%m-%d)
python3 "$HOME/.openclaw/workspace/daily-memory-aggregator.py" "$TODAY"
echo ""

echo "=== Memory File Check ==="
echo "Hourly summaries:"
ls -la "$HOME/.openclaw/workspace/memory/hourly/"
echo ""

echo "Daily memories:"
ls -la "$HOME/.openclaw/workspace/memory/"
echo ""

echo "=== Setup Cron Jobs ==="
echo "Setting up hourly job..."
bash "$HOME/.openclaw/workspace/setup-hourly-memory-cron.sh"
echo ""

echo "Setting up daily job..."
bash "$HOME/.openclaw/workspace/setup-daily-memory-cron.sh"
echo ""

echo "=== Crontab Check ==="
crontab -l | grep -E "hourly-memory-summarizer|daily-memory-aggregator"
echo ""

echo "=== Test Complete ==="