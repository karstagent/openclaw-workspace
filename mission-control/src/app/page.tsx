import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-4 bg-black">
      <div className="glass-container max-w-md p-8 text-center">
        <h1 className="text-3xl font-bold mb-4 text-content">Mission Control</h1>
        <p className="mb-6 text-content-muted">
          Welcome to Mission Control, your comprehensive dashboard for managing tasks and monitoring system status.
        </p>
        <Link
          href="/dashboard/kanban"
          className="glass-button-primary inline-flex items-center"
        >
          <span>Enter Dashboard</span>
          <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}