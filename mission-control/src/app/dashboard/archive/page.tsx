'use client';

import React from 'react';
import ArchiveSystem from '@/components/archive/ArchiveSystem';

export default function ArchivePage() {
  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-content">Message Archive</h2>
        <p className="text-content-muted">Browse and manage archived messages and reports</p>
      </div>
      <ArchiveSystem />
    </div>
  );
}