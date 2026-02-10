'use client';

import React, { useState } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Task, TaskCategory } from '@/types/kanban';
import { formatDate, cn } from '@/lib/utils';
import { Edit, Trash2, MoreVertical, ArrowUp, CheckCircle, Briefcase, Code, Search, FileText, Cog, ClipboardList, HelpCircle } from 'lucide-react';
import { useKanbanStore } from '@/store/kanbanStore';
import TaskForm from './TaskForm';

interface KanbanTaskProps {
  task: Task;
  index: number;
  isDragging?: boolean;
}

const KanbanTask: React.FC<KanbanTaskProps> = ({ task, index, isDragging }) => {
  const [showOptions, setShowOptions] = useState(false);
  const [editing, setEditing] = useState(false);
  
  // Find column ID for this task
  const { board, deleteTask } = useKanbanStore();
  const columnId = board.columns.find((column) => 
    column.tasks.some((t) => t.id === task.id)
  )?.id;

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({
    id: task.id,
    data: {
      type: 'task',
      task,
      index,
    },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getPriorityClass = () => {
    switch (task.priority) {
      case 'low':
        return 'task-priority-low';
      case 'medium':
        return 'task-priority-medium';
      case 'high':
        return 'task-priority-high';
      case 'critical':
        return 'task-priority-critical';
      default:
        return '';
    }
  };
  
  const getCategoryIcon = () => {
    switch (task.category) {
      case 'business':
        return <Briefcase className="h-4 w-4 text-blue-400" />;
      case 'development':
        return <Code className="h-4 w-4 text-green-400" />;
      case 'research':
        return <Search className="h-4 w-4 text-purple-400" />;
      case 'content':
        return <FileText className="h-4 w-4 text-yellow-400" />;
      case 'automation':
        return <Cog className="h-4 w-4 text-orange-400" />;
      case 'admin':
        return <ClipboardList className="h-4 w-4 text-red-400" />;
      default:
        return <HelpCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const handleEdit = () => {
    setEditing(true);
    setShowOptions(false);
  };

  const handleDelete = () => {
    if (columnId) {
      deleteTask(columnId, task.id);
    }
    setShowOptions(false);
  };

  if (editing && columnId) {
    return <TaskForm task={task} columnId={columnId} onClose={() => setEditing(false)} />;
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'kanban-task',
        getPriorityClass(),
        isDragging && 'task-dragging'
      )}
      {...attributes}
      {...listeners}
    >
      <div className="relative">
        <div className="flex justify-between items-start">
          <div className="flex items-start gap-2">
            <div className="mt-0.5">
              {getCategoryIcon()}
            </div>
            <h4 className="text-sm font-semibold text-content mb-2">{task.title}</h4>
          </div>
          <div className="relative">
            <button 
              className="p-1 rounded-full hover:bg-glass-light text-content-muted"
              onClick={() => setShowOptions(!showOptions)}
              aria-label="Task options"
            >
              <MoreVertical className="h-4 w-4" />
            </button>
            
            {showOptions && (
              <div className="absolute right-0 mt-1 w-36 glass-container z-10 p-1">
                <button 
                  className="flex items-center w-full p-2 text-xs rounded hover:bg-glass-light text-content-muted text-left"
                  onClick={handleEdit}
                >
                  <Edit className="h-3 w-3 mr-2" />
                  Edit Task
                </button>
                <button 
                  className="flex items-center w-full p-2 text-xs rounded hover:bg-glass-light text-danger-light text-left"
                  onClick={handleDelete}
                >
                  <Trash2 className="h-3 w-3 mr-2" />
                  Delete Task
                </button>
              </div>
            )}
          </div>
        </div>
        
        <p className="text-xs text-content-muted mb-3 line-clamp-2">
          {task.description}
        </p>
        
        <div className="flex justify-between items-end">
          <div>
            {task.priority === 'high' || task.priority === 'critical' ? (
              <span className={cn(
                'glass-badge',
                task.priority === 'critical' ? 'glass-badge-danger' : 'glass-badge-warning',
                'flex items-center'
              )}>
                <ArrowUp className="h-3 w-3 mr-1" />
                {task.priority}
              </span>
            ) : (
              <span className="text-xs text-content-subtle">
                {task.estimatedHours && `${task.estimatedHours}h`}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {task.assignedTo && (
              <span className="text-xs bg-glass-light px-1.5 py-0.5 rounded text-content-muted">
                {task.assignedTo}
              </span>
            )}
            
            {task.completedDate && (
              <span className="flex items-center text-xs text-success-light">
                <CheckCircle className="h-3 w-3 mr-1" />
                {formatDate(task.completedDate)}
              </span>
            )}
            
            {task.progress !== undefined && !task.completedDate && (
              <div className="w-16 h-1.5 bg-glass-lighter rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary-light"
                  style={{ width: `${task.progress}%` }}
                ></div>
              </div>
            )}
          </div>
        </div>
        
        {task.tags && task.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {task.tags.map(tag => (
              <span key={tag} className="text-xs bg-glass-dark px-1.5 py-0.5 rounded text-content-subtle">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default KanbanTask;