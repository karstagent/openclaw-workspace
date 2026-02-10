'use client';

import React, { useState, useEffect } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { SortableContext, arrayMove, rectSortingStrategy } from '@dnd-kit/sortable';
import { useKanbanStore } from '@/store/kanbanStore';
import KanbanColumn from './KanbanColumn';
import KanbanTask from './KanbanTask';
import { ColumnId, Task } from '@/types/kanban';
import { Plus, RefreshCw } from 'lucide-react';
import TaskForm from './TaskForm';
import KanbanSyncStatus from './KanbanSyncStatus';
import CurrentTaskStatus from './CurrentTaskStatus';
import { useKanbanDataLoader } from '@/lib/loadKanbanData';

const KanbanBoard: React.FC = () => {
  const { board, moveTask, loadKanbanData } = useKanbanStore();
  const [activeTask, setActiveTask] = useState<{ task: Task; columnId: ColumnId } | null>(null);
  const [showAddTask, setShowAddTask] = useState(false);
  const [addToColumn, setAddToColumn] = useState<ColumnId | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Use our custom hook to load data
  useKanbanDataLoader();
  
  // Function to manually refresh the data
  const refreshKanbanData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/kanban-data', {
        cache: 'no-store', // Prevent caching
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      if (response.ok) {
        const data = await response.json();
        loadKanbanData(data);
        console.log('Kanban data refreshed:', data);
      } else {
        console.error('Error response from server:', response.status);
      }
    } catch (error) {
      console.error('Error refreshing kanban data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Set up auto-refresh every 5 seconds
  useEffect(() => {
    const intervalId = setInterval(() => {
      refreshKanbanData();
    }, 5000);
    
    // Initial load
    refreshKanbanData();
    
    return () => clearInterval(intervalId);
  }, []);
  
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const { id } = active;

    const taskId = id.toString();
    let foundTask: Task | undefined;
    let foundColumnId: ColumnId | undefined;

    // Find the task and its column
    for (const column of board.columns) {
      const task = column.tasks.find((t) => t.id === taskId);
      if (task) {
        foundTask = task;
        foundColumnId = column.id;
        break;
      }
    }

    if (foundTask && foundColumnId) {
      setActiveTask({
        task: foundTask,
        columnId: foundColumnId,
      });
    }
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    // If the task is being dragged over a different column
    if (overId.toString().startsWith('column-')) {
      const overColumnId = overId.toString().replace('column-', '') as ColumnId;
      
      // Find current column and task
      let sourceColumnId: ColumnId | undefined;
      let sourceIndex: number = -1;

      for (const column of board.columns) {
        const taskIndex = column.tasks.findIndex((t) => t.id === activeId);
        if (taskIndex !== -1) {
          sourceColumnId = column.id;
          sourceIndex = taskIndex;
          break;
        }
      }

      if (sourceColumnId && sourceColumnId !== overColumnId && sourceIndex !== -1) {
        // Move to the end of the target column
        const destIndex = board.columns.find(c => c.id === overColumnId)?.tasks.length || 0;
        moveTask(activeId.toString(), 
          { columnId: sourceColumnId, index: sourceIndex }, 
          { columnId: overColumnId, index: destIndex }
        );
      }
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) {
      setActiveTask(null);
      return;
    }

    const activeId = active.id;
    const overId = over.id;

    // Find source column and index
    let sourceColumnId: ColumnId | undefined;
    let sourceIndex: number = -1;
    let destinationColumnId: ColumnId | undefined;
    let destinationIndex: number = -1;

    // First, find the source column and task index
    for (const column of board.columns) {
      const taskIndex = column.tasks.findIndex((t) => t.id === activeId);
      if (taskIndex !== -1) {
        sourceColumnId = column.id;
        sourceIndex = taskIndex;
        break;
      }
    }

    // Check if dropping on a task
    if (!overId.toString().startsWith('column-')) {
      // Find destination column and index
      for (const column of board.columns) {
        const taskIndex = column.tasks.findIndex((t) => t.id === overId);
        if (taskIndex !== -1) {
          destinationColumnId = column.id;
          destinationIndex = taskIndex;
          break;
        }
      }
    } else {
      // Dropping directly on a column
      destinationColumnId = overId.toString().replace('column-', '') as ColumnId;
      destinationIndex = board.columns.find(c => c.id === destinationColumnId)?.tasks.length || 0;
    }

    if (
      sourceColumnId &&
      sourceIndex !== -1 &&
      destinationColumnId &&
      destinationIndex !== -1
    ) {
      moveTask(
        activeId.toString(),
        { columnId: sourceColumnId, index: sourceIndex },
        { columnId: destinationColumnId, index: destinationIndex }
      );
    }

    setActiveTask(null);
  };

  const handleAddTask = (columnId: ColumnId) => {
    setAddToColumn(columnId);
    setShowAddTask(true);
  };

  return (
    <div className="p-4">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold text-content mb-2">Project Tasks</h2>
            <p className="text-content-muted">
              Drag and drop tasks between columns to update their status
            </p>
          </div>
          <button 
            onClick={refreshKanbanData} 
            className="glass-button p-2 rounded-full"
            disabled={isLoading}
          >
            <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        <KanbanSyncStatus />
      </div>
      
      {/* Current Task Status Bar */}
      <CurrentTaskStatus refreshInterval={3000} />

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex space-x-6 overflow-x-auto pb-4">
          {board.columns.map((column) => (
            <SortableContext
              key={column.id}
              items={column.tasks.map((task) => task.id)}
              strategy={rectSortingStrategy}
            >
              <KanbanColumn
                column={column}
                onAddTask={() => handleAddTask(column.id)}
              />
            </SortableContext>
          ))}
        </div>

        <DragOverlay>
          {activeTask && (
            <KanbanTask task={activeTask.task} index={-1} isDragging />
          )}
        </DragOverlay>
      </DndContext>

      {showAddTask && addToColumn && (
        <TaskForm
          columnId={addToColumn}
          onClose={() => {
            setShowAddTask(false);
            setAddToColumn(null);
          }}
        />
      )}

      <div className="mt-8">
        <button
          onClick={() => handleAddTask('backlog')}
          className="glass-button-primary flex items-center"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add New Task
        </button>
      </div>
    </div>
  );
};

export default KanbanBoard;