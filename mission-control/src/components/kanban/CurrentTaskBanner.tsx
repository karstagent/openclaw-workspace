'use client';

import React, { useEffect, useState } from 'react';

const CurrentTaskBanner: React.FC = () => {
  const [taskStatus, setTaskStatus] = useState<string>('Loading current task...');
  const [isVisible, setIsVisible] = useState<boolean>(true);

  useEffect(() => {
    const fetchTaskStatus = async () => {
      try {
        // Read the current task status from a local file (for demo purposes)
        const response = await fetch(`/api/current-task-status?t=${Date.now()}`);
        if (response.ok) {
          const data = await response.json();
          if (data.currentTaskStatus) {
            setTaskStatus(data.currentTaskStatus);
          }
        }
      } catch (error) {
        console.error('Error fetching task status:', error);
      }
    };

    // Fetch immediately
    fetchTaskStatus();

    // Then set up interval to fetch every few seconds
    const intervalId = setInterval(fetchTaskStatus, 2000);

    return () => clearInterval(intervalId);
  }, []);

  if (!isVisible) return null;

  return (
    <div className="glass-container p-4 mb-4 bg-primary/10 relative">
      <button 
        className="absolute top-2 right-2 text-content-muted hover:text-content"
        onClick={() => setIsVisible(false)}
      >
        ×
      </button>
      <h3 className="text-sm font-medium text-content-muted mb-1">CURRENT TASK</h3>
      <p className="text-xl font-semibold text-content">{taskStatus}</p>
    </div>
  );
};

export default CurrentTaskBanner;