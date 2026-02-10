# How to Access Mission Control

The Mission Control UI is now set up and running. To access it, follow these steps:

## Option 1: Use Direct URLs

The Mission Control UI should be available at one of these URLs (try each in order):

1. http://localhost:3000
2. http://localhost:3001
3. http://localhost:3002

Open your browser and navigate to each URL until you find the one that works.

## Option 2: Check the Next.js Console Output

When running the Mission Control server, look at the console output from the Next.js server. 
It will display a line like:
```
- Local:        http://localhost:3000
```
Use that URL to access the Mission Control UI.

## Option 3: Restart the Servers

If you're having trouble accessing the UI, you can restart both servers with:

```bash
# Kill existing servers
pkill -f "next dev"
pkill -f "convex dev"

# Start the servers again
cd /Users/karst/.openclaw/workforce/mission-control && npx convex dev &
cd /Users/karst/.openclaw/workforce/mission-control && npm run dev &
```

Then check the console output to determine the correct URL.

## Task Creation

Once you access the Mission Control UI:

1. Navigate to the "Overview" tab
2. Click the "New Task" button in the top-right corner
3. Fill in the task details and assign it to Pip
4. Click "Create Task" to save

## Troubleshooting

If you encounter any issues:

1. Check that both the Convex and Next.js servers are running
2. Ensure you're using the correct URL as shown in the Next.js console output
3. If the UI loads but task creation doesn't work, it might be an issue with the Convex database connection

For detailed instructions on task workflows, see `/Users/karst/.openclaw/workspace/task_workflow.md`