# Mission Control Task Assignment Fix

I've identified the issue with the Mission Control task assignment functionality. The problem occurs because the code is trying to use the string "pip" as an agent ID, but the database expects a valid ID reference from the agents table.

## The Fix

1. First, let's add Pip to the agents table if not already present:

Create a script in `/Users/karst/.openclaw/workforce/mission-control/scripts/add_pip_agent.js`:

```javascript
const { ConvexHttpClient } = require("convex/browser");
const { api } = require("../convex/_generated/api");

// Create a Convex client
const client = new ConvexHttpClient("http://127.0.0.1:3211");

async function addPipAgent() {
  try {
    // Check if Pip already exists
    const agents = await client.query(api.agents.list);
    const pipAgent = agents.find(agent => agent.name.toLowerCase() === "pip");
    
    if (pipAgent) {
      console.log("Pip agent already exists with ID:", pipAgent._id);
      return pipAgent._id;
    }
    
    // Add Pip agent
    const newAgentId = await client.mutation(api.agents.create, {
      name: "Pip",
      role: "Assistant",
      status: "active",
      description: "Autonomous digital partner",
      sessionKey: "pip",
      avatar: "/images/pip-avatar.png"
    });
    
    console.log("Created Pip agent with ID:", newAgentId);
    return newAgentId;
  } catch (error) {
    console.error("Error adding Pip agent:", error);
    throw error;
  }
}

addPipAgent();
```

2. Then fix the NewTaskModal component in `/Users/karst/.openclaw/workforce/mission-control/src/components/NewTaskModal.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from "convex/react";
import { api } from "../../convex/_generated/api";

interface NewTaskModalProps {
  onClose: () => void;
  onAddTask: (task: any) => void;
}

export default function NewTaskModal({ onClose, onAddTask }: NewTaskModalProps) {
  const [taskName, setTaskName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [assignedTo, setAssignedTo] = useState(''); // Store agent ID instead of name
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Get agents list
  const agents = useQuery(api.agents.list) || [];
  
  // Get the create task mutation from Convex
  const createTask = useMutation(api.tasks.create);
  
  // Set default agent (Pip) when agents list loads
  useEffect(() => {
    if (agents.length > 0) {
      const pipAgent = agents.find(agent => agent.name.toLowerCase() === "pip");
      if (pipAgent) {
        setAssignedTo(pipAgent._id);
      }
    }
  }, [agents]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Format date for storage if provided
      let dueDateTimestamp = undefined;
      if (dueDate) {
        dueDateTimestamp = new Date(dueDate).getTime();
      }
      
      // Create the task in the database
      const taskId = await createTask({
        title: taskName,
        description: description,
        status: assignedTo ? 'assigned' : 'inbox', // Set status based on assignment
        priority: priority as 'low' | 'medium' | 'high' | 'urgent',
        dueDate: dueDateTimestamp,
        assigneeIds: assignedTo ? [assignedTo] : [], // Use the actual ID
      });
      
      // Find the agent name for display
      const assigneeName = assignedTo ? 
        agents.find(a => a._id === assignedTo)?.name : 
        undefined;
      
      // Pass the new task to parent component with generated ID
      onAddTask({
        id: taskId,
        title: taskName,
        description,
        status: assignedTo ? 'assigned' : 'inbox',
        priority,
        dueDate: dueDate,
        assignee: assigneeName,
        createdAt: new Date().toISOString()
      });
      
      // Close the modal
      onClose();
    } catch (error) {
      console.error("Failed to create task:", error);
      alert("Failed to create task. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="glass rounded-lg max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Create New Task</h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Close modal"
            disabled={isSubmitting}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="taskName" className="block text-sm font-medium mb-1">Task Name</label>
            <input
              id="taskName"
              type="text"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              className="glass-input w-full"
              placeholder="Enter task name"
              required
              disabled={isSubmitting}
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium mb-1">Description</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="glass-input w-full h-24 resize-none"
              placeholder="Describe the task..."
              disabled={isSubmitting}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="priority" className="block text-sm font-medium mb-1">Priority</label>
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="glass-input w-full"
                disabled={isSubmitting}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="dueDate" className="block text-sm font-medium mb-1">Due Date (Optional)</label>
              <input
                id="dueDate"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="glass-input w-full"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Assign To</label>
            <select
              id="assignedTo"
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
              className="glass-input w-full"
              disabled={isSubmitting || agents.length === 0}
            >
              <option value="">Unassigned</option>
              {agents.map(agent => (
                <option key={agent._id} value={agent._id}>
                  {agent.name}
                </option>
              ))}
            </select>
            {agents.length === 0 && (
              <p className="text-sm text-yellow-500 mt-1">Loading agents...</p>
            )}
          </div>
          
          <div className="mt-6 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors duration-200"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`glass-button px-4 py-2 rounded-md hover-lift ${isSubmitting ? 'opacity-75 cursor-not-allowed' : ''}`}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

3. Also, we need to add a create function to the agents.ts file if it doesn't already exist:

```typescript
// Add to convex/agents.ts

// Create a new agent
export const create = mutation({
  args: {
    name: v.string(),
    role: v.string(),
    status: v.string(),
    description: v.string(),
    sessionKey: v.string(),
    avatar: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const agentId = await ctx.db.insert("agents", {
      name: args.name,
      role: args.role,
      status: args.status,
      description: args.description,
      sessionKey: args.sessionKey,
      avatar: args.avatar,
      lastActive: Date.now(),
    });
    
    // Log this activity
    await ctx.db.insert("activities", {
      type: "agent_created",
      agentId,
      message: `Created agent: ${args.name}`,
      timestamp: Date.now(),
    });
    
    return agentId;
  },
});
```

## Steps to Apply the Fix

1. Add the missing create function to the agents.ts file
2. Update the NewTaskModal component with the fixed code
3. Run the add_pip_agent.js script to ensure Pip exists in the database
4. Restart the Mission Control service

After making these changes, the task assignment should work correctly.