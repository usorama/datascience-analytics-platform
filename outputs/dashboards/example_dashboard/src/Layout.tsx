import React, { ReactNode } from 'react';
import { FilterPanel } from './FilterPanel';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Filter Panel - Fixed */}
      <aside className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
        <FilterPanel />
      </aside>
      
      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
};