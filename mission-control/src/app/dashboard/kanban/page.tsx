'use client';

import React from 'react';
import KanbanBoard from '@/components/kanban/KanbanBoard';
import CurrentTaskBanner from '@/components/kanban/CurrentTaskBanner';

export default function KanbanPage() {
  return (
    <div className="container mx-auto">
      <CurrentTaskBanner />
      <KanbanBoard />
    </div>
  );
}