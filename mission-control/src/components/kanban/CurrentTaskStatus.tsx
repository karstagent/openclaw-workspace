'use client';

import React, { useEffect, useState } from 'react';

interface CurrentTaskStatusProps {
  refreshInterval?: number; // in milliseconds
}

const CurrentTaskStatus: React.FC<CurrentTaskStatusProps> = ({
  refreshInterval = 5000, // Default to checking every 5 seconds
}) => {
  const [currentTask, setCurrentTask] = useState<string>('Initializing task status...');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Function to fetch the current task status
  const fetchCurrentTaskStatus = async () => {
    try {
      // Read the JSON file with the kanban board data
      const response = await fetch('/api/current-task-status');
      if (response.ok) {
        const data = await response.json();
        setCurrentTask(data.currentTaskStatus || 'No active task');
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error('Error fetching current task status:', error);
      setCurrentTask('Error loading task status');
    }
  };

  // Fetch on component mount
  useEffect(() => {
    fetchCurrentTaskStatus();
    
    // Set up interval for periodic updates
    const intervalId = setInterval(fetchCurrentTaskStatus, refreshInterval);
    
    // Clear interval on component unmount
    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  return (
    <div className="glass-container p-3 mb-4 flex items-center justify-between">
      <div>
        <h3 className="text-sm font-medium text-content-muted mb-1">CURRENT TASK</h3>
        <p className="text-lg font-semibold text-content">{currentTask}</p>
      </div>
      {lastUpdated && (
        <div className="text-xs text-content-subtle">
          Updated: {lastUpdated}
        </div>
      )}
    </div>
  );
};

export default CurrentTaskStatus;