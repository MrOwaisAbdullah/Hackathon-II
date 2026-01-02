'use client';

import React from 'react';
import { Sidebar } from '@/components/dashboard/Sidebar';
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
        <Sidebar />

        <main className="flex-1 overflow-y-auto relative scroll-smooth">
          <div className="p-8 max-w-7xl mx-auto w-full">
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
