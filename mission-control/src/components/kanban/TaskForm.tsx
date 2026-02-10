'use client';

import React, { useState } from 'react';
import { ColumnId, Task, TaskPriority, TaskCategory } from '@/types/kanban';
import { useKanbanStore } from '@/store/kanbanStore';
import { X, Tags } from 'lucide-react';

interface TaskFormProps {
  task?: Task;
  columnId: ColumnId;
  onClose: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ task, columnId, onClose }) => {
  const { addTask, updateTask } = useKanbanStore();
  const isEditing = !!task;
  
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 'medium' as TaskPriority,
    category: task?.category || 'other' as TaskCategory,
    estimatedHours: task?.estimatedHours || undefined,
    progress: task?.progress || undefined,
    assignedTo: task?.assignedTo || 'Pip',
    assignedBy: task?.assignedBy || 'Jordan',
    dueDate: task?.dueDate || '',
    tags: task?.tags?.join(', ') || '',
    notes: task?.notes || '',
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'estimatedHours' || name === 'progress') {
      const numValue = value === '' ? undefined : Number(value);
      setFormData(prev => ({ ...prev, [name]: numValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Process tags into an array if provided
    const processedData = {
      ...formData,
      tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : undefined
    };
    
    if (isEditing && task) {
      updateTask(columnId, task.id, processedData);
    } else {
      addTask(columnId, processedData);
    }
    
    onClose();
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="glass-container w-full max-w-lg p-6 relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 glass-button p-1 rounded-full"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
        
        <h3 className="text-xl font-semibold mb-4 text-content">
          {isEditing ? 'Edit Task' : 'Add New Task'}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-content-muted mb-1">
              Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="glass-input w-full"
              required
            />
          </div>
          
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-content-muted mb-1">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="glass-input w-full h-24"
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-content-muted mb-1">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="glass-select w-full"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-content-muted mb-1">
                Category
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="glass-select w-full"
              >
                <option value="business">Business</option>
                <option value="development">Development</option>
                <option value="research">Research</option>
                <option value="content">Content</option>
                <option value="automation">Automation</option>
                <option value="admin">Admin</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="estimatedHours" className="block text-sm font-medium text-content-muted mb-1">
                Estimated Hours
              </label>
              <input
                type="number"
                id="estimatedHours"
                name="estimatedHours"
                value={formData.estimatedHours || ''}
                onChange={handleChange}
                className="glass-input w-full"
                min="0"
                step="0.5"
              />
            </div>
            
            <div>
              <label htmlFor="dueDate" className="block text-sm font-medium text-content-muted mb-1">
                Due Date
              </label>
              <input
                type="date"
                id="dueDate"
                name="dueDate"
                value={formData.dueDate}
                onChange={handleChange}
                className="glass-input w-full"
              />
            </div>
          </div>
          
          {(columnId === 'in-progress' || columnId === 'testing') && (
            <div>
              <label htmlFor="progress" className="block text-sm font-medium text-content-muted mb-1">
                Progress (%)
              </label>
              <input
                type="number"
                id="progress"
                name="progress"
                value={formData.progress || ''}
                onChange={handleChange}
                className="glass-input w-full"
                min="0"
                max="100"
              />
            </div>
          )}
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="assignedTo" className="block text-sm font-medium text-content-muted mb-1">
                Assigned To
              </label>
              <select
                id="assignedTo"
                name="assignedTo"
                value={formData.assignedTo}
                onChange={handleChange}
                className="glass-select w-full"
              >
                <option value="Pip">Pip</option>
                <option value="Jordan">Jordan</option>
                <option value="Both">Both</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="assignedBy" className="block text-sm font-medium text-content-muted mb-1">
                Assigned By
              </label>
              <select
                id="assignedBy"
                name="assignedBy"
                value={formData.assignedBy}
                onChange={handleChange}
                className="glass-select w-full"
              >
                <option value="Jordan">Jordan</option>
                <option value="Pip">Pip</option>
              </select>
            </div>
          </div>
          
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-content-muted mb-1">
              Tags (comma-separated)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Tags className="h-4 w-4 text-content-muted" />
              </div>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleChange}
                className="glass-input w-full pl-10"
                placeholder="e.g., urgent, research, follow-up"
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-content-muted mb-1">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              className="glass-input w-full h-16"
              placeholder="Additional details or context..."
            />
          </div>
          
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="glass-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="glass-button-primary"
            >
              {isEditing ? 'Save Changes' : 'Add Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskForm;