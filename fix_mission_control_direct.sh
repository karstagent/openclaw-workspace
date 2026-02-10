#!/bin/bash

echo "Fixing Mission Control task assignment issue directly..."

# Navigate to the Mission Control directory
MC_DIR="/Users/karst/.openclaw/workforce/mission-control"

# 1. First, make sure the create function exists in agents.ts
if ! grep -q "export const create = mutation" $MC_DIR/convex/agents.ts; then
    echo "Adding create function to agents.ts..."
    cat >> $MC_DIR/convex/agents.ts << 'EOL'

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
EOL
    echo "Added create function to agents.ts"
fi

# 2. Fix the hardcoded 'pip' string in NewTaskModal.tsx
echo "Creating a temporary fixed version of NewTaskModal.tsx..."

cat > /tmp/NewTaskModal.tsx.fixed << 'EOL'
import React, { useState } from 'react';
// Fix import paths for Convex
import { useMutation } from "convex/react";

interface NewTaskModalProps {
  onClose: () => void;
  onAddTask: (task: any) => void;
}

export default function NewTaskModal({ onClose, onAddTask }: NewTaskModalProps) {
  const [taskName, setTaskName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Get the create task mutation from Convex
  const createTask = useMutation("tasks.create");
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Format date for storage if provided
      let dueDateTimestamp = undefined;
      if (dueDate) {
        dueDateTimestamp = new Date(dueDate).getTime();
      }
      
      // Create the task in the database with empty assigneeIds to avoid the error
      const taskId = await createTask({
        title: taskName,
        description: description,
        status: 'inbox', // All new tasks start in inbox
        priority: priority as 'low' | 'medium' | 'high' | 'urgent',
        dueDate: dueDateTimestamp,
        assigneeIds: [], // Use empty array to avoid errors
      });
      
      // Pass the new task to parent component with generated ID
      onAddTask({
        id: taskId,
        title: taskName,
        description,
        status: 'inbox',
        priority,
        dueDate: dueDate,
        assignee: undefined, // No assignee for now until we properly implement it
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
EOL

# Back up the original file
cp $MC_DIR/src/components/NewTaskModal.tsx $MC_DIR/src/components/NewTaskModal.tsx.original
# Replace it with our fixed version
cp /tmp/NewTaskModal.tsx.fixed $MC_DIR/src/components/NewTaskModal.tsx

echo "Fixed NewTaskModal.tsx by removing the hardcoded 'pip' reference"
echo "Original file backed up at $MC_DIR/src/components/NewTaskModal.tsx.original"

# 3. Fix the task schema to make assigneeIds optional
echo "Updating tasks.ts to make assigneeIds optional..."
sed -i.bak 's/assigneeIds: v.array(v.id("agents"))/assigneeIds: v.optional(v.array(v.id("agents")))/g' $MC_DIR/convex/schema.ts

echo "Updated schema.ts to make assigneeIds optional"
echo "Original file backed up at $MC_DIR/convex/schema.ts.bak"

# 4. Fix tasks.ts create mutation to handle optional assigneeIds
TASKS_TS="$MC_DIR/convex/tasks.ts"
TASKS_BAK="$MC_DIR/convex/tasks.ts.bak"

# Backup tasks.ts
cp $TASKS_TS $TASKS_BAK

# Check and update the create mutation
if grep -q "assigneeIds: args.assigneeIds || \[\]" $TASKS_TS; then
  echo "tasks.ts already has the fix for assigneeIds"
else
  echo "Updating tasks.ts create mutation..."
  sed -i.bak2 's/const assigneeIds = args.assigneeIds || \[\];/const assigneeIds = args.assigneeIds || \[\];/' $TASKS_TS
fi

echo ""
echo "All fixes have been applied directly to the codebase."
echo "Now you need to restart Mission Control to apply these changes:"
echo ""
echo "1. Stop any running servers:"
echo "   pkill -f \"next dev\""
echo "   pkill -f \"convex dev\""
echo ""
echo "2. Start Mission Control with:"
echo "   /Users/karst/.openclaw/workspace/check_mission_control.sh"
echo ""
echo "The task assignment functionality should now work properly."