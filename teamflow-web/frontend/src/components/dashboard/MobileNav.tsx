'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { Menu, LayoutDashboard, FolderKanban, CheckSquare, Users, Clock, Archive, Settings, LogOut } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sheet, SheetHeader, SheetContent } from '@/components/ui/sheet';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
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

export function MobileNav() {
  const [open, setOpen] = React.useState(false);
  const pathname = usePathname();
  const { logout, user } = useAuth();

  return (
    <>
      {/* Hamburger Button (visible only on mobile) */}
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(true)}
        className="lg:hidden p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-foreground transition-colors"
        aria-label="Open menu"
      >
        <Menu size={24} />
      </motion.button>

      {/* Mobile Sheet/Drawer */}
      <Sheet open={open} onOpenChange={setOpen} side="left">
        {/* Header */}
        <SheetHeader title="Menu" onClose={() => setOpen(false)} />

        {/* Content */}
        <SheetContent>
          <div className="space-y-6">
            {/* User Profile */}
            <div className="flex items-center gap-3 p-4 bg-secondary rounded-lg">
              <div className="w-12 h-12 rounded-full bg-lime-500 flex items-center justify-center text-white font-bold">
                {user?.name?.[0] || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground truncate">{user?.name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="space-y-1">
              {menuItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                  >
                    <motion.div
                      whileTap={{ scale: 0.98 }}
                      className={`flex items-center gap-3 px-4 py-4 rounded-lg transition-colors ${
                        isActive
                          ? 'text-black bg-lime-500 font-semibold'
                          : 'text-muted-foreground hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-foreground'
                      }`}
                    >
                      <item.icon size={22} className="shrink-0" />
                      <span className="text-base">{item.label}</span>
                    </motion.div>
                  </Link>
                );
              })}
            </nav>

            {/* Divider */}
            <div className="border-t border-border" />

            {/* Theme Toggle */}
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-sm font-medium text-foreground">Theme</span>
              <ThemeToggle />
            </div>

            {/* Logout Button */}
            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                logout();
                setOpen(false);
              }}
              className="w-full flex items-center gap-3 px-4 py-4 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 font-medium transition-colors"
            >
              <LogOut size={22} />
              <span>Logout</span>
            </motion.button>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
