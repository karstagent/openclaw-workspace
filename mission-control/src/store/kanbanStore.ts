import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Board, ColumnId, Task } from '@/types/kanban';

// Initial data directly loaded from kanban-board.json
const defaultBoard: Board = {
  "lastUpdated": "2026-02-08T20:30:00-08:00",
  "columns": [
    {
      "id": "backlog",
      "title": "To Do",
      "tasks": []
    },
    {
      "id": "in-progress",
      "title": "In Progress",
      "tasks": []
    },
    {
      "id": "testing",
      "title": "Review",
      "tasks": [
        {
          "id": "openclaw-automation-research",
          "title": "Research Advanced OpenClaw Agent Automation Techniques",
          "description": "Comprehensive research on advanced automation strategies for OpenClaw agents, including multi-agent systems, intelligent scheduling, memory optimization, and model selection",
          "priority": "high",
          "category": "research",
          "estimatedHours": 3,
          "progress": 100,
          "assignedTo": "Pip",
          "assignedBy": "Jordan",
          "tags": ["automation", "research", "openclaw"],
          "createdAt": "2026-02-08T20:17:00-08:00",
          "notes": "Created comprehensive documentation in openclaw-advanced-automation.md covering multi-agent orchestration, intelligent scheduling, memory optimization, model selection strategies, and implementation roadmap."
        }
      ]
    },
    {
      "id": "completed",
      "title": "Done",
      "tasks": []
    }
  ]
};

// Define store interface
interface KanbanStore {
  board: Board;
  
  // Actions
  moveTask: (
    taskId: string,
    source: { columnId: ColumnId; index: number },
    destination: { columnId: ColumnId; index: number }
  ) => void;
  
  addTask: (columnId: ColumnId, task: Omit<Task, 'id' | 'createdAt'>) => void;
  updateTask: (columnId: ColumnId, taskId: string, updates: Partial<Task>) => void;
  deleteTask: (columnId: ColumnId, taskId: string) => void;
  
  updateColumn: (columnId: ColumnId, newTitle: string) => void;
  
  loadKanbanData: (data: Board) => void;
}

// Create the store
// Helper function to save board to the server
const saveToServer = async (board: Board) => {
  try {
    await fetch('/api/kanban-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(board),
    });
    console.log('Saved to server:', board);
  } catch (error) {
    console.error('Failed to save to server:', error);
  }
};

export const useKanbanStore = create<KanbanStore>()(
  persist(
    (set) => ({
      board: defaultBoard,
      
      moveTask: (taskId, source, destination) => 
        set((state) => {
          const newBoard = { ...state.board };
          
          // Get all columns
          const columns = [...newBoard.columns];
          
          // Get source and destination columns
          const sourceColumn = columns.find((col) => col.id === source.columnId);
          const destColumn = columns.find((col) => col.id === destination.columnId);
          
          if (!sourceColumn || !destColumn) return state;
          
          // Get the task
          const taskToMove = sourceColumn.tasks[source.index];
          
          // If moving to completed column, add completion date
          if (destination.columnId === 'completed' && !taskToMove.completedDate) {
            taskToMove.completedDate = new Date().toISOString().split('T')[0];
          }
          
          // If moving from completed column, remove completion date
          if (source.columnId === 'completed' && destination.columnId !== 'completed') {
            delete taskToMove.completedDate;
          }
          
          // Remove from source
          sourceColumn.tasks.splice(source.index, 1);
          
          // Add to destination
          destColumn.tasks.splice(destination.index, 0, taskToMove);
          
          newBoard.lastUpdated = new Date().toISOString();
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
      
      addTask: (columnId, taskData) => 
        set((state) => {
          const newBoard = { ...state.board };
          const column = newBoard.columns.find((col) => col.id === columnId);
          
          if (!column) return state;
          
          // Create new task with ID and createdAt
          const task: Task = {
            id: `task-${Date.now()}`,
            createdAt: new Date().toISOString(),
            ...taskData,
          };
          
          // Add to column
          column.tasks.push(task);
          newBoard.lastUpdated = new Date().toISOString();
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
      
      updateTask: (columnId, taskId, updates) => 
        set((state) => {
          const newBoard = { ...state.board };
          const column = newBoard.columns.find((col) => col.id === columnId);
          
          if (!column) return state;
          
          // Find task index
          const taskIndex = column.tasks.findIndex((task) => task.id === taskId);
          
          if (taskIndex === -1) return state;
          
          // Update task
          column.tasks[taskIndex] = {
            ...column.tasks[taskIndex],
            ...updates,
          };
          
          newBoard.lastUpdated = new Date().toISOString();
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
      
      deleteTask: (columnId, taskId) => 
        set((state) => {
          const newBoard = { ...state.board };
          const column = newBoard.columns.find((col) => col.id === columnId);
          
          if (!column) return state;
          
          // Filter out the task
          column.tasks = column.tasks.filter((task) => task.id !== taskId);
          
          newBoard.lastUpdated = new Date().toISOString();
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
      
      updateColumn: (columnId, newTitle) => 
        set((state) => {
          const newBoard = { ...state.board };
          const column = newBoard.columns.find((col) => col.id === columnId);
          
          if (!column) return state;
          
          // Update column title
          column.title = newTitle;
          
          newBoard.lastUpdated = new Date().toISOString();
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
      
      loadKanbanData: (data) => 
        set(() => {
          const newBoard = {
            ...data,
            lastUpdated: new Date().toISOString(),
          };
          
          // Save to server
          saveToServer(newBoard);
          
          return { board: newBoard };
        }),
    }),
    {
      name: 'kanban-store',
    }
  )
);