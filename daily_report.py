#!/usr/bin/env python3
import os
import datetime
import json
import subprocess

def send_report():
    """Generate and send a daily report"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Count files modified in the last 24 hours
    cmd = f"find /Users/karst/.openclaw/workspace/glasswall-rebuild -type f -mtime -1 | wc -l"
    modified_files = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    
    # Generate report
    report = f"""
# Daily Development Report: {today}

## Project: GlassWall

### Activity Summary
- Files modified in the last 24 hours: {modified_files}
- Current focus: Message queue system and UI components

### Next Steps
1. Complete webhook implementation
2. Test batch processing system
3. Set up deployment pipeline

### Resources
- Project directory: /Users/karst/.openclaw/workspace/glasswall-rebuild
- Log directory: /Users/karst/.openclaw/workspace/logs
    """
    
    # Save report
    report_dir = "/Users/karst/.openclaw/workspace/reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_path = os.path.join(report_dir, f"report_{today}.md")
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"Daily report saved to {report_path}")
    
    # Attempt to send the report via OpenClaw message tool
    try:
        openclaw_cmd = f"openclaw message -e 'Daily Development Report: {today}' -b @{report_path} send --to telegram:535786496"
        subprocess.run(openclaw_cmd, shell=True)
        print("Report sent via OpenClaw message tool")
    except Exception as e:
        print(f"Failed to send report: {str(e)}")

if __name__ == "__main__":
    send_report()