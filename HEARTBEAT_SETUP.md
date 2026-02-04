# Heartbeat Setup - DO NOT DELETE

## Active Heartbeat Cron Job

**Status:** ✅ ACTIVE  
**Job ID:** 69d90079-77b1-4a26-b829-2b0f00a4f93b  
**Frequency:** Every 5 minutes (300,000ms)  
**Target:** Main session  

## How to Verify

Check if heartbeat cron is running:
```bash
# From OpenClaw CLI or tool
cron({ action: "list" })
```

Should show a job named "Heartbeat - 5 minute updates" with enabled: true.

## How to Check Status

```bash
# List all cron jobs
cron({ action: "list" })

# Get specific job details
cron({ action: "status" })
```

## Heartbeat Behavior

Every 5 minutes, Karst will:
1. Read HEARTBEAT.md for instructions
2. Follow the checklist (rotate through monitoring tasks)
3. Reply with progress updates if working on something
4. Reply with HEARTBEAT_OK if nothing needs attention

## If Heartbeat Stops Working

1. Check if job still exists: `cron({ action: "list" })`
2. If missing, recreate with:
   ```javascript
   cron({
     action: "add",
     job: {
       name: "Heartbeat - 5 minute updates",
       schedule: { kind: "every", everyMs: 300000 },
       payload: {
         kind: "systemEvent",
         text: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
       },
       sessionTarget: "main",
       enabled: true
     }
   })
   ```
3. Check HEARTBEAT.md exists and has proper instructions
4. Check gateway status: `openclaw gateway status`

## Configuration Files

- **HEARTBEAT.md** - Instructions for what to check during heartbeats
- **HEARTBEAT_SETUP.md** (this file) - Documentation for maintaining the cron job
- **memory/heartbeat-state.json** - Tracks last check times (if used)

## Important Notes

- This cron job is PERSISTENT across gateway restarts
- If you manually delete it, it won't auto-recreate
- The job fires even when no one is chatting
- Updates go to the main Telegram session

## Last Setup Date

Created: 2026-02-03 21:20 PST  
By: Karst (after user requested persistent 5-minute updates)
