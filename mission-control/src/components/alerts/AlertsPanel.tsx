'use client';

import React, { useState } from 'react';
import { AlertCircle, Bell, Check, Clock, Info, X } from 'lucide-react';
import { formatDate } from '@/lib/utils';

export type AlertType = 'info' | 'success' | 'warning' | 'error';

export interface Alert {
  id: string;
  title: string;
  message: string;
  type: AlertType;
  timestamp: string;
  isRead: boolean;
  isAcknowledged: boolean;
  source?: string;
}

const getAlertIcon = (type: AlertType) => {
  switch (type) {
    case 'info':
      return <Info className="h-5 w-5 text-primary" />;
    case 'success':
      return <Check className="h-5 w-5 text-success" />;
    case 'warning':
      return <AlertCircle className="h-5 w-5 text-warning" />;
    case 'error':
      return <AlertCircle className="h-5 w-5 text-danger" />;
  }
};

const getAlertClass = (type: AlertType) => {
  switch (type) {
    case 'info':
      return 'border-l-primary/50';
    case 'success':
      return 'border-l-success/50';
    case 'warning':
      return 'border-l-warning/50';
    case 'error':
      return 'border-l-danger/50';
  }
};

interface AlertsPanelProps {
  onClose?: () => void;
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ onClose }) => {
  // Sample data
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: 'a1',
      title: 'System Update Completed',
      message: 'The system has been successfully updated to version 2.3.0.',
      type: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      isRead: false,
      isAcknowledged: false,
      source: 'System'
    },
    {
      id: 'a2',
      title: 'Database Performance Warning',
      message: 'Database query times exceeding threshold. Consider optimization.',
      type: 'warning',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      isRead: true,
      isAcknowledged: false,
      source: 'Database'
    },
    {
      id: 'a3',
      title: 'New Task Assigned',
      message: 'You have been assigned to the task "Implement Real-time Sync".',
      type: 'info',
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      isRead: true,
      isAcknowledged: true,
      source: 'Task Management'
    },
    {
      id: 'a4',
      title: 'API Error Detected',
      message: 'Failed connection attempts to external API. Check network settings.',
      type: 'error',
      timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
      isRead: false,
      isAcknowledged: false,
      source: 'API Gateway'
    },
    {
      id: 'a5',
      title: 'Scheduled Maintenance',
      message: 'System maintenance scheduled for 2:00 AM. Expected downtime: 15 minutes.',
      type: 'info',
      timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
      isRead: true,
      isAcknowledged: false,
      source: 'System'
    }
  ]);

  const [filter, setFilter] = useState<AlertType | 'all'>('all');
  
  const markAsRead = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, isRead: true } : alert
    ));
  };
  
  const acknowledgeAlert = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, isAcknowledged: true } : alert
    ));
  };
  
  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  const markAllAsRead = () => {
    setAlerts(alerts.map(alert => ({ ...alert, isRead: true })));
  };
  
  const clearAllAcknowledged = () => {
    setAlerts(alerts.filter(alert => !alert.isAcknowledged));
  };
  
  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.type === filter);
  
  const unreadCount = alerts.filter(alert => !alert.isRead).length;

  return (
    <div className="glass-container rounded-glass p-4 w-full max-w-3xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <Bell className="h-5 w-5 mr-2 text-content" />
          <h2 className="text-xl font-semibold text-content">
            Alerts {unreadCount > 0 && <span className="text-sm ml-2 glass-badge-primary">{unreadCount} unread</span>}
          </h2>
        </div>
        
        {onClose && (
          <button 
            onClick={onClose}
            className="glass-button p-1 rounded-full"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      
      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
        <button 
          onClick={() => setFilter('all')}
          className={`glass-button text-xs px-3 py-1 ${filter === 'all' ? 'bg-glass-highlight text-content' : ''}`}
        >
          All
        </button>
        <button 
          onClick={() => setFilter('info')}
          className={`glass-button text-xs px-3 py-1 ${filter === 'info' ? 'bg-primary/20 text-primary-light' : ''}`}
        >
          Info
        </button>
        <button 
          onClick={() => setFilter('success')}
          className={`glass-button text-xs px-3 py-1 ${filter === 'success' ? 'bg-success/20 text-success-light' : ''}`}
        >
          Success
        </button>
        <button 
          onClick={() => setFilter('warning')}
          className={`glass-button text-xs px-3 py-1 ${filter === 'warning' ? 'bg-warning/20 text-warning-light' : ''}`}
        >
          Warnings
        </button>
        <button 
          onClick={() => setFilter('error')}
          className={`glass-button text-xs px-3 py-1 ${filter === 'error' ? 'bg-danger/20 text-danger-light' : ''}`}
        >
          Errors
        </button>
        <div className="flex-1"></div>
        <button 
          onClick={markAllAsRead}
          className="glass-button text-xs px-3 py-1"
        >
          Mark all read
        </button>
        <button 
          onClick={clearAllAcknowledged}
          className="glass-button text-xs px-3 py-1"
        >
          Clear acknowledged
        </button>
      </div>
      
      <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8 text-content-muted">
            <Bell className="h-8 w-8 mx-auto mb-2 opacity-40" />
            <p>No alerts to display</p>
          </div>
        ) : (
          filteredAlerts.map(alert => (
            <div 
              key={alert.id}
              className={`glass-card relative border-l-4 ${getAlertClass(alert.type)} ${!alert.isRead ? 'glass-shimmer' : ''}`}
              onClick={() => markAsRead(alert.id)}
            >
              <div className="flex items-start">
                <div className="mr-3 mt-0.5">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-content mb-1">{alert.title}</h3>
                  <p className="text-xs text-content-muted mb-2">{alert.message}</p>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center text-xs text-content-subtle">
                      <Clock className="h-3 w-3 mr-1" />
                      <span>{formatDate(alert.timestamp)}</span>
                      {alert.source && (
                        <span className="ml-2 glass-badge text-xs">{alert.source}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      {!alert.isAcknowledged && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            acknowledgeAlert(alert.id);
                          }}
                          className="text-xs glass-button px-2 py-0.5"
                        >
                          Acknowledge
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteAlert(alert.id);
                        }}
                        className="text-xs glass-button-danger px-2 py-0.5"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPanel;