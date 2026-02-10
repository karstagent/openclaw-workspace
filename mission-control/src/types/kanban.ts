export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskCategory = 'business' | 'development' | 'research' | 'content' | 'automation' | 'admin' | 'other';

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: TaskPriority;
  category?: TaskCategory; 
  estimatedHours?: number;
  progress?: number;
  assignedTo?: string;
  assignedBy?: string;
  dueDate?: string;
  tags?: string[];
  createdAt: string;
  completedDate?: string;
  notes?: string;
}

export type ColumnId = 'backlog' | 'in-progress' | 'testing' | 'completed';

export interface Column {
  id: ColumnId;
  title: string;
  tasks: Task[];
}

export interface Board {
  columns: Column[];
  lastUpdated: string;
}

export type DragEndEvent = {
  active: { id: string; data?: { current?: { columnId?: ColumnId; index?: number } } };
  over?: { id: string; data?: { current?: { columnId?: ColumnId; index?: number } } };
};

export type ActiveTask = {
  id: string;
  data: {
    task: Task;
    columnId: ColumnId;
    index: number;
  };
};

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  status: 'online' | 'offline' | 'busy' | 'away';
}

export interface SystemStatus {
  id: string;
  name: string;
  status: 'operational' | 'degraded' | 'outage' | 'maintenance';
  uptime: number; // percentage
  lastIncident?: string; // ISO date string
}

export interface Metric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number; // percentage change
  history: number[]; // array of historical values for charts
}

export interface Notification {
  id: string;
  title: string;
  description: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string; // ISO date string
  read: boolean;
}

export interface Activity {
  id: string;
  user: string;
  action: string;
  target: string;
  timestamp: string; // ISO date string
}

export interface Resource {
  id: string;
  name: string;
  type: 'agent' | 'database' | 'api' | 'storage' | 'compute';
  usage: number; // percentage
  limit: number;
  unit: string;
}