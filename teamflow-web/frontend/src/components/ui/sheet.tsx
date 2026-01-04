'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface SheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  side?: 'left' | 'right' | 'top' | 'bottom';
}

export function Sheet({ open, onOpenChange, children, side = 'left' }: SheetProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => onOpenChange(false)}
          />

          {/* Sheet */}
          <motion.div
            initial={
              side === 'left'
                ? { x: '-100%' }
                : side === 'right'
                  ? { x: '100%' }
                  : side === 'top'
                    ? { y: '-100%' }
                    : { y: '100%' }
            }
            animate={{ x: 0, y: 0 }}
            exit={
              side === 'left'
                ? { x: '-100%' }
                : side === 'right'
                  ? { x: '100%' }
                  : side === 'top'
                    ? { y: '-100%' }
                    : { y: '100%' }
            }
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={`fixed z-50 bg-card border border-border shadow-xl h-full w-80 ${
              side === 'left' ? 'left-0 top-0' : side === 'right' ? 'right-0 top-0' : side === 'top' ? 'top-0 left-0 right-0' : 'bottom-0 left-0 right-0'
            }`}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface SheetHeaderProps {
  title: string;
  onClose: () => void;
}

export function SheetHeader({ title, onClose }: SheetHeaderProps) {
  return (
    <div className="flex items-center justify-between p-6 border-b border-border">
      <h2 className="text-lg font-bold text-foreground">{title}</h2>
      <button
        onClick={onClose}
        className="p-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-muted-foreground hover:text-foreground transition-colors"
      >
        <X size={20} />
      </button>
    </div>
  );
}

interface SheetContentProps {
  children: React.ReactNode;
}

export function SheetContent({ children }: SheetContentProps) {
  return <div className="flex-1 overflow-y-auto p-4">{children}</div>;
}
