import { useState, useEffect } from 'react';
import { getKanbanData, updateKanbanData } from '../lib/api';

export default function KanbanBoard() {
  const [boardData, setBoardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load data on component mount
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await getKanbanData();
        setBoardData(data);
        setLoading(false);
        setError(null);
      } catch (err) {
        console.error('Failed to load board data:', err);
        setError('Failed to load projects');
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Save board data when it changes
  const saveBoard = async (updatedData) => {
    try {
      await updateKanbanData(updatedData);
      setBoardData(updatedData);
    } catch (err) {
      console.error('Failed to save board data:', err);
      setError('Failed to save changes');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-pulse text-blue-500 font-mono text-xl">
          Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <div className="bg-red-600 text-white p-6 rounded-lg shadow-lg glass-panel">
          <h2 className="text-2xl font-bold mb-2">Error:</h2>
          <ul className="list-disc pl-5">
            <li>{error}</li>
          </ul>
        </div>
        <p className="mt-4 text-gray-300">
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>
    );
  }

  if (!boardData) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <div className="bg-yellow-600 text-white p-6 rounded-lg shadow-lg glass-panel">
          <h2 className="text-2xl font-bold mb-2">Warning:</h2>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-white">
        Mission Control Kanban Board
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {boardData.columns.map((column) => (
          <div key={column.id} className="glass-panel p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-white">
              {column.title}
            </h2>
            <div className="space-y-3">
              {column.tasks.map((task) => (
                <div
                  key={task.id}
                  className="glass-card p-3 rounded"
                >
                  <h3 className="font-medium text-white">{task.title}</h3>
                  {task.progress !== undefined && (
                    <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500"
                        style={{ width: `${task.progress}%` }}
                      ></div>
                    </div>
                  )}
                  <div className="text-xs text-gray-300 mt-2">
                    {task.assignedTo && (
                      <span className="mr-2">Assigned: {task.assignedTo}</span>
                    )}
                    {task.priority && (
                      <span
                        className={`px-1.5 py-0.5 rounded ${
                          task.priority === 'high'
                            ? 'bg-red-900 text-red-100'
                            : task.priority === 'medium'
                            ? 'bg-yellow-900 text-yellow-100'
                            : 'bg-blue-900 text-blue-100'
                        }`}
                      >
                        {task.priority}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 text-sm text-gray-400">
        <p>Last updated: {new Date(boardData.lastUpdated).toLocaleString()}</p>
      </div>
    </div>
  );
}