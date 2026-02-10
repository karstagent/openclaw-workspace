# Access Mission Control

The Mission Control UI is now set up and running! You can access it at:

## The UI is Ready at: http://localhost:3000

Simply open your browser and navigate to this URL to access the Mission Control dashboard.

## Using the Task Management System

1. **Create a Task for Pip:**
   - Click the "New Task" button in the top-right corner
   - Fill out the task details (title, description, priority, etc.)
   - In the "Assign To" dropdown, select "Pip"
   - Click "Create Task" to save

2. **Monitor Task Progress:**
   - Tasks will appear in their respective columns based on status
   - Pip will update the status as work progresses
   - You can manually move tasks between columns by dragging them

## If You Need to Restart

If you need to restart the Mission Control servers:

```bash
# Run the check script
/Users/karst/.openclaw/workspace/check_mission_control.sh
```

This will:
1. Stop any existing Mission Control processes
2. Start the Convex database server
3. Start the Next.js frontend
4. Open the UI in your browser

## Troubleshooting

If you encounter any issues:

1. Check that both servers are running with:
   ```bash
   ps aux | grep -i "next\|convex" | grep -v grep
   ```

2. Try restarting everything:
   ```bash
   pkill -f "next dev"
   pkill -f "convex dev"
   /Users/karst/.openclaw/workspace/check_mission_control.sh
   ```

3. Verify the application is accessible with:
   ```bash
   curl -I http://localhost:3000
   ```

For detailed instructions on task workflows, see `/Users/karst/.openclaw/workspace/task_workflow.md`