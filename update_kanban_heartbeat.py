import os
import json
from datetime import datetime

# Update heartbeat state after completing a check
def update_heartbeat_state(check_name):
    state_path = "/Users/karst/.openclaw/workspace/memory/heartbeat-state.json"
    
    try:
        # Read current state
        with open(state_path, 'r') as f:
            state = json.load(f)
        
        # Update timestamp for the check
        current_time = int(datetime.now().timestamp())
        state["lastChecks"][check_name] = current_time
        
        # Write updated state back
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
            
        # Log the update
        log_dir = "/Users/karst/.openclaw/workspace/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        with open(f"{log_dir}/heartbeat.log", 'a') as log:
            log.write(f"[{datetime.now().isoformat()}] Completed {check_name} check\n")
            
        return True
        
    except Exception as e:
        print(f"Error updating heartbeat state: {str(e)}")
        return False

# Update the kanban check
update_heartbeat_state("kanban")