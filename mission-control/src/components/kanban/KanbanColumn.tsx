'use client';

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { Column } from '@/types/kanban';
import KanbanTask from './KanbanTask';
import { SortableContext, rectSortingStrategy } from '@dnd-kit/sortable';
import { Plus } from 'lucide-react';

interface KanbanColumnProps {
  column: Column;
  onAddTask: () => void;
}

const KanbanColumn: React.FC<KanbanColumnProps> = ({ column, onAddTask }) => {
  const { setNodeRef } = useDroppable({
    id: `column-${column.id}`,
  });

  return (
    <div
      ref={setNodeRef}
      className="kanban-column flex flex-col"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-content">
          {column.title} ({column.tasks.length})
        </h3>
        <button
          onClick={onAddTask}
          className="p-1 rounded-full glass-button-primary"
          aria-label={`Add task to ${column.title}`}
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <SortableContext items={column.tasks.map(task => task.id)} strategy={rectSortingStrategy}>
          {column.tasks.map((task, index) => (
            <KanbanTask key={task.id} task={task} index={index} />
          ))}
        </SortableContext>

        {column.tasks.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 p-4 border border-dashed border-glass rounded-glass text-content-subtle">
            <p className="text-sm text-center mb-2">No tasks</p>
            <button 
              onClick={onAddTask}
              className="text-xs glass-button"
            >
              Add task
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default KanbanColumn;