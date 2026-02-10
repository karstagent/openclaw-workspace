'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { 
  BarChart3, 
  Bell, 
  ChevronLeft, 
  ChevronRight, 
  Home, 
  LayoutDashboard, 
  LogOut, 
  Menu, 
  MessageSquare, 
  Settings, 
  Users, 
  ListTodo,
  X,
  AlertCircle,
  Archive,
  Activity
} from 'lucide-react';
import Link from 'next/link';

interface NavItemProps {
  icon: React.ReactNode;
  title: string;
  href: string;
  isActive?: boolean;
  onClick?: () => void;
}

const NavItem: React.FC<NavItemProps> = ({ 
  icon, 
  title, 
  href, 
  isActive = false,
  onClick 
}) => {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center rounded-glass p-3 text-content-muted hover:text-content hover:bg-glass-light transition-all duration-300 ease-in-out mb-1',
        isActive && 'bg-glass-highlight text-primary border-glass-highlight'
      )}
      onClick={onClick}
    >
      <div className="mr-3">{icon}</div>
      <span className="font-medium text-sm">{title}</span>
    </Link>
  );
};

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };
  
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };
  
  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-black flex">
      {/* Desktop Sidebar */}
      <aside 
        className={cn(
          'hidden md:flex md:flex-col glass-container border-r-0 h-screen sticky top-0 transition-all duration-300 ease-in-out',
          collapsed ? 'w-[80px]' : 'w-[260px]'
        )}
      >
        <div className="flex items-center p-4 border-b border-glass">
          <div className={cn(
            'flex items-center',
            collapsed ? 'justify-center' : 'justify-between w-full'
          )}>
            {!collapsed && (
              <h1 className="font-bold text-xl text-content">Mission Control</h1>
            )}
            
            <button 
              onClick={toggleSidebar}
              className="glass-button p-1 rounded-full"
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>
          </div>
        </div>

        <div className="flex-1 flex flex-col justify-between overflow-y-auto p-3">
          <nav>
            {collapsed ? (
              <div className="flex flex-col items-center space-y-3 py-3">
                <Link href="/dashboard" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <Home size={20} />
                </Link>
                <Link href="/dashboard/kanban" className="p-2 rounded-full bg-glass-highlight text-primary border border-glass-highlight">
                  <ListTodo size={20} />
                </Link>
                <Link href="/dashboard/metrics" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <Activity size={20} />
                </Link>
                <Link href="/dashboard/alerts" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <AlertCircle size={20} />
                </Link>
                <Link href="/dashboard/archive" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <Archive size={20} />
                </Link>
                <Link href="/dashboard/analytics" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <BarChart3 size={20} />
                </Link>
                <Link href="/dashboard/team" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <Users size={20} />
                </Link>
              </div>
            ) : (
              <div className="space-y-1">
                <NavItem icon={<Home size={18} />} title="Overview" href="/dashboard" />
                <NavItem icon={<ListTodo size={18} />} title="Kanban Board" href="/dashboard/kanban" isActive />
                <NavItem icon={<Activity size={18} />} title="Live Metrics" href="/dashboard/metrics" />
                <NavItem icon={<AlertCircle size={18} />} title="Alert Management" href="/dashboard/alerts" />
                <NavItem icon={<Archive size={18} />} title="Message Archive" href="/dashboard/archive" />
                <NavItem icon={<BarChart3 size={18} />} title="Analytics" href="/dashboard/analytics" />
                <NavItem icon={<MessageSquare size={18} />} title="Messages" href="/dashboard/messages" />
                <NavItem icon={<Users size={18} />} title="Team" href="/dashboard/team" />
              </div>
            )}
          </nav>

          <div className={collapsed ? 'flex flex-col items-center space-y-3 pt-3' : 'mt-auto'}>
            {!collapsed && <div className="glass-divider my-2" />}
            
            {collapsed ? (
              <>
                <Link href="/dashboard/settings" className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <Settings size={20} />
                </Link>
                <button className="p-2 rounded-full hover:bg-glass-light text-content-muted hover:text-content">
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <>
                <NavItem icon={<Settings size={18} />} title="Settings" href="/dashboard/settings" />
                <button className="flex items-center rounded-glass p-3 text-content-muted hover:text-danger hover:bg-glass-light transition-colors duration-300 w-full mb-1">
                  <LogOut size={18} className="mr-3" />
                  <span className="font-medium text-sm">Logout</span>
                </button>
              </>
            )}
          </div>
        </div>
      </aside>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-80 z-40 md:hidden" 
          onClick={closeMobileMenu}
        />
      )}

      {/* Mobile Sidebar */}
      <aside 
        className={cn(
          'fixed inset-y-0 left-0 glass-container w-[260px] z-50 md:hidden transition-transform duration-300',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-glass">
          <h1 className="font-bold text-xl text-content">Mission Control</h1>
          <button 
            onClick={closeMobileMenu}
            className="glass-button p-1 rounded-full"
            aria-label="Close menu"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-3">
          <nav className="space-y-1">
            <NavItem 
              icon={<Home size={18} />} 
              title="Overview" 
              href="/dashboard" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<ListTodo size={18} />} 
              title="Kanban Board" 
              href="/dashboard/kanban" 
              isActive 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<Activity size={18} />} 
              title="Live Metrics" 
              href="/dashboard/metrics" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<AlertCircle size={18} />} 
              title="Alert Management" 
              href="/dashboard/alerts" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<Archive size={18} />} 
              title="Message Archive" 
              href="/dashboard/archive" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<BarChart3 size={18} />} 
              title="Analytics" 
              href="/dashboard/analytics" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<MessageSquare size={18} />} 
              title="Messages" 
              href="/dashboard/messages" 
              onClick={closeMobileMenu}
            />
            <NavItem 
              icon={<Users size={18} />} 
              title="Team" 
              href="/dashboard/team" 
              onClick={closeMobileMenu}
            />

            <div className="glass-divider my-4" />

            <NavItem 
              icon={<Settings size={18} />} 
              title="Settings" 
              href="/dashboard/settings" 
              onClick={closeMobileMenu}
            />
            <button className="flex items-center rounded-glass p-3 text-content-muted hover:text-danger hover:bg-glass-light transition-colors duration-300 w-full">
              <LogOut size={18} className="mr-3" />
              <span className="font-medium text-sm">Logout</span>
            </button>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Nav */}
        <header className="glass-container border-b border-glass p-4 sticky top-0 z-30">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button 
                className="glass-button p-2 rounded-full md:hidden mr-2"
                onClick={toggleMobileMenu}
                aria-label="Open menu"
              >
                <Menu size={20} />
              </button>
              <h2 className="text-lg font-semibold text-content">Kanban Board</h2>
            </div>

            <div className="flex items-center space-x-3">
              <button className="glass-button p-2 rounded-full relative">
                <Bell size={18} />
                <span className="absolute top-0 right-0 w-2 h-2 rounded-full bg-primary"></span>
              </button>
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
                <span className="text-white text-xs font-bold">JK</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>

        {/* Footer */}
        <footer className="glass-container border-t border-glass p-4 text-content-subtle text-xs">
          <div className="flex justify-between items-center">
            <p>© 2026 Mission Control</p>
            <p>Liquid Glass Interface</p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default DashboardLayout;