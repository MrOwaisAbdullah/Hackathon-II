
'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Users,
  Clock,
  Settings,
  ChevronLeft,
  LogOut,
  Menu,
  Archive
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { UserAvatar } from '@/components/ui/UserAvatar';
import { useAuth } from '@/hooks/useAuth';

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: FolderKanban, label: 'Projects', href: '/projects' },
  { icon: CheckSquare, label: 'Tasks', href: '/tasks' },
  { icon: Users, label: 'Team', href: '/team' },
  { icon: Clock, label: 'Time', href: '/time-entries' },
  { icon: Archive, label: 'Archive', href: '/archive' },
  { icon: Settings, label: 'Settings', href: '/settings' },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const pathname = usePathname();
  const { logout, user } = useAuth();

  // Persist collapse state
  React.useEffect(() => {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState) {
      setIsCollapsed(savedState === 'true');
    }
  }, []);

  const toggleSidebar = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem('sidebarCollapsed', String(newState));
  };

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 80 : 280 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="h-screen sidebar-dark z-20 flex flex-col relative border-r"
    >
      {/* Header */}
      <div className={`h-16 flex items-center border-b border-zinc-800 px-4 ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="font-bold text-xl text-white tracking-tight flex items-center gap-2"
            >
              <div className="w-2 h-2 rounded-full bg-lime-400" />
              TeamFlow
            </motion.div>
          )}
        </AnimatePresence>
        
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-white"
        >
          {isCollapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* User Profile (Mini) */}
      <div className="p-4 border-b border-zinc-800">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
          <UserAvatar
            name={user?.name}
            email={user?.email}
            size="lg"
            className="shrink-0"
          />
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden"
              >
                <p className="font-medium text-sm truncate text-white">{user?.name}</p>
                <p className="text-xs text-zinc-400 truncate">{user?.email}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto px-2 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                className={`flex items-center py-3 rounded-lg transition-colors relative ${
                  isCollapsed ? 'justify-center px-0' : 'gap-3 px-3'
                } ${
                  isActive 
                    ? 'text-black bg-lime-400 font-medium' 
                    : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
                }`}
                whileHover={{ x: isCollapsed ? 0 : 4 }}
                whileTap={{ scale: 0.98 }}
              >
                <item.icon size={20} className="shrink-0" />
                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      className="whitespace-nowrap overflow-hidden"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800 flex flex-col gap-2">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          {!isCollapsed && <span className="text-sm font-medium text-zinc-400">Theme</span>}
          {/* Note: ThemeToggle needs adjustment for dark sidebar context */}
          <div className="opacity-50 hover:opacity-100 transition-opacity">
             <ThemeToggle />
          </div>
        </div>
        
        <button 
          onClick={() => logout()}
          className={`flex items-center py-3 rounded-lg text-rose-400 hover:bg-rose-900/20 transition-colors w-full mt-2 ${
            isCollapsed ? 'justify-center px-0' : 'gap-3 px-3'
          }`}
        >
          <LogOut size={20} className="shrink-0" />
          {!isCollapsed && <span>Logout</span>}
        </button>
      </div>
    </motion.aside>
  );
}
