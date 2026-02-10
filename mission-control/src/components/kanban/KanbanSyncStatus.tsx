'use client';

import React from 'react';
import useRealTimeSync, { SyncStatus } from '@/hooks/useRealTimeSync';
import { CheckCircle, Cloud, CloudOff, Loader, RefreshCw } from 'lucide-react';
import { formatDate } from '@/lib/utils';

const KanbanSyncStatus: React.FC = () => {
  const syncStatus = useRealTimeSync();

  return (
    <div className="glass-card mb-4 flex items-center justify-between p-3">
      <div className="flex items-center">
        {syncStatus.connected ? (
          <Cloud className="h-5 w-5 text-success mr-2" />
        ) : (
          <CloudOff className="h-5 w-5 text-warning mr-2" />
        )}
        
        <div>
          <h3 className="text-sm font-medium text-content">
            {syncStatus.connected ? 'Connected' : 'Disconnected'}
          </h3>
          <p className="text-xs text-content-muted">
            {syncStatus.lastSyncTime 
              ? `Last synchronized: ${formatDate(syncStatus.lastSyncTime)}`
              : 'Not yet synchronized'}
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {syncStatus.pendingChanges > 0 && (
          <span className="glass-badge text-xs">
            {syncStatus.pendingChanges} pending {syncStatus.pendingChanges === 1 ? 'change' : 'changes'}
          </span>
        )}

        {syncStatus.syncing ? (
          <div className="flex items-center text-primary-light text-xs">
            <Loader className="h-3 w-3 mr-1 animate-spin" />
            <span>Syncing...</span>
          </div>
        ) : syncStatus.connected && syncStatus.lastSyncTime ? (
          <div className="flex items-center text-success-light text-xs">
            <CheckCircle className="h-3 w-3 mr-1" />
            <span>Up to date</span>
          </div>
        ) : null}

        <button 
          className="glass-button p-1.5 rounded-full"
          aria-label="Refresh synchronization"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>
      </div>

      {syncStatus.syncError && (
        <div className="absolute bottom-full left-0 right-0 glass-badge-danger mb-1 py-1 px-2 text-xs text-center">
          {syncStatus.syncError}
        </div>
      )}
    </div>
  );
};

export default KanbanSyncStatus;