#!/bin/bash

echo "Testing task status updates..."

# Update with different statuses
/Users/karst/.openclaw/workspace/task-status-updater.py "Testing task status banner (1/5): Initial test"
sleep 2
/Users/karst/.openclaw/workspace/task-status-updater.py "Testing task status banner (2/5): Adding progress indicators"
sleep 2
/Users/karst/.openclaw/workspace/task-status-updater.py "Testing task status banner (3/5): Implementing auto-refresh functionality"
sleep 2
/Users/karst/.openclaw/workspace/task-status-updater.py "Testing task status banner (4/5): Styling and visual enhancements"
sleep 2
/Users/karst/.openclaw/workspace/task-status-updater.py "Testing task status banner (5/5): Final verification complete"

echo "Test completed. Banner should now show the final status."