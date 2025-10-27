'use client';

import { useState, ReactNode } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

interface DashboardLayoutProps {
  children: ReactNode;
  title?: string;
}

export default function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Topbar */}
        <Topbar onMenuClick={() => setSidebarOpen(true)} title={title} />

        {/* Page content */}
        <main className="py-8 px-6 sm:px-8 lg:px-10">
          {children}
        </main>
      </div>
    </div>
  );
}
