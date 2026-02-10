#!/bin/bash

# Schedule the background task to run every hour
echo "Setting up hourly development task..."
(crontab -l 2>/dev/null; echo "0 * * * * cd /Users/karst/.openclaw/workspace && python autonomous_task.py >> logs/cron.log 2>&1") | crontab -

# Schedule a daily report at 9 AM
echo "Setting up daily report..."
(crontab -l 2>/dev/null; echo "0 9 * * * cd /Users/karst/.openclaw/workspace && python daily_report.py >> logs/report.log 2>&1") | crontab -

echo "Scheduled jobs have been set up."