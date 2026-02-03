#!/bin/bash
# Daily Briefing Generator
# Summarizes overnight work, costs, and priorities

set -e

WORKSPACE="/Users/karst/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
OUTPUT="$WORKSPACE/tracking/daily-briefing-$DATE.md"

echo "# Daily Briefing - $DATE" > "$OUTPUT"
echo "" >> "$OUTPUT"

# Cost Summary
echo "## 💰 Cost Summary" >> "$OUTPUT"
echo "" >> "$OUTPUT"
if [ -f "$WORKSPACE/scripts/cost-calculator.js" ]; then
  node "$WORKSPACE/scripts/cost-calculator.js" >> "$OUTPUT" 2>&1 || echo "Cost calculation unavailable" >> "$OUTPUT"
else
  echo "Cost tracker not yet implemented" >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"

# Activity Log (last 24 hours)
echo "## 📋 Recent Activity" >> "$OUTPUT"
echo "" >> "$OUTPUT"
if [ -f "$WORKSPACE/tracking/activity-log.jsonl" ]; then
  echo "Recent events:" >> "$OUTPUT"
  tail -20 "$WORKSPACE/tracking/activity-log.jsonl" | while read line; do
    echo "- $line" >> "$OUTPUT"
  done
else
  echo "No activity log found" >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"

# Status
echo "## 🎯 Current Status" >> "$OUTPUT"
echo "" >> "$OUTPUT"
if [ -f "$WORKSPACE/STATUS.md" ]; then
  cat "$WORKSPACE/STATUS.md" >> "$OUTPUT"
else
  echo "Status file not found" >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"

# Git changes
echo "## 🔨 Work Completed" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cd "$WORKSPACE"
if [ -d .git ]; then
  echo "Recent commits:" >> "$OUTPUT"
  git log --oneline --since="24 hours ago" >> "$OUTPUT" 2>&1 || echo "No recent commits" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  echo "Modified files:" >> "$OUTPUT"
  git status --short >> "$OUTPUT" 2>&1 || echo "No changes" >> "$OUTPUT"
else
  echo "Not a git repository" >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"

# Output location
echo "Briefing saved to: $OUTPUT"
cat "$OUTPUT"
