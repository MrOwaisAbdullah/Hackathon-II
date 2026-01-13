'use client';

import React from 'react';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { MobileNav } from '@/components/dashboard/MobileNav';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { CommandPalette } from '@/components/CommandPalette';
import { motion } from 'framer-motion';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background text-foreground transition-colors duration-300">
        {/* Desktop Sidebar - hidden on mobile */}
        <div className="hidden lg:block">
          <Sidebar />
        </div>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto relative scroll-smooth">
          {/* Mobile Header */}
          <div className="lg:hidden sticky top-0 z-30 bg-card border-b border-border px-3 sm:px-4 py-3 flex items-center gap-2 sm:gap-3">
            <MobileNav />
            <h1 className="font-bold text-base sm:text-lg text-foreground truncate">TeamFlow</h1>
          </div>

          {/* Page Content */}
          <div className="p-4 sm:p-6 md:p-8 pb-16 sm:pb-20 max-w-7xl mx-auto w-full">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              {children}
            </motion.div>
          </div>
        </main>

        {/* T157: Command Palette - available on all pages */}
        <CommandPalette />
      </div>
    </ProtectedRoute>
  );
}
