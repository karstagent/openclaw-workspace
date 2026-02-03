#!/bin/bash
# Karst Dashboard - Quick status overview

clear
echo "🪨 KARST DASHBOARD"
echo "═══════════════════════════════════════════════════"
echo ""

# Current Status
if [ -f "/Users/karst/.openclaw/workspace/STATUS.md" ]; then
  echo "📊 CURRENT STATUS"
  echo "─────────────────────────────────────────────────"
  head -20 "/Users/karst/.openclaw/workspace/STATUS.md"
  echo ""
fi

# Cost Summary
echo "💰 COST SUMMARY"
echo "─────────────────────────────────────────────────"
if [ -f "/Users/karst/.openclaw/workspace/scripts/cost-calculator.js" ]; then
  node "/Users/karst/.openclaw/workspace/scripts/cost-calculator.js" 2>&1 | head -10
else
  echo "Cost calculator not available"
fi
echo ""

# Recent Activity
echo "📋 RECENT ACTIVITY"
echo "─────────────────────────────────────────────────"
if [ -f "/Users/karst/.openclaw/workspace/tracking/activity-log.jsonl" ]; then
  tail -5 "/Users/karst/.openclaw/workspace/tracking/activity-log.jsonl" | while read line; do
    timestamp=$(echo "$line" | jq -r '.timestamp // empty' 2>/dev/null)
    event=$(echo "$line" | jq -r '.event // empty' 2>/dev/null)
    if [ -n "$event" ]; then
      echo "• $event ($timestamp)"
    fi
  done
else
  echo "No activity log yet"
fi
echo ""

# Git Status
echo "🔨 WORKSPACE STATUS"
echo "─────────────────────────────────────────────────"
cd "/Users/karst/.openclaw/workspace"
if [ -d .git ]; then
  git status --short | head -10
  [ $? -ne 0 ] && echo "Clean working directory"
else
  echo "Not tracking changes"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "Run 'node scripts/cost-calculator.js' for detailed cost breakdown"
echo "Run 'cat STATUS.md' for full status"
echo "Run 'tail tracking/activity-log.jsonl' for recent activity"
