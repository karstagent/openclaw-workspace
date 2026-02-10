'use client';

import React from 'react';
import AlertsPanel from '@/components/alerts/AlertsPanel';

export default function AlertsPage() {
  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-content">Alert Management</h2>
        <p className="text-content-muted">Monitor system notifications and manage alerts</p>
      </div>
      <AlertsPanel />
    </div>
  );
}