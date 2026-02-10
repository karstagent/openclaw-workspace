'use client';

import React from 'react';
import MetricsWidget from '@/components/dashboard-metrics/MetricsWidget';

export default function MetricsPage() {
  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-content">System Metrics</h2>
        <p className="text-content-muted">Real-time performance monitoring and analytics</p>
      </div>
      <MetricsWidget />
    </div>
  );
}