'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw, ArrowLeft } from 'lucide-react';

/**
 * T154: Error Boundary for the main app section
 *
 * This catches errors in the dashboard, tasks, projects, etc.
 * and allows users to retry or go back.
 */

export default function MainAppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Main app error:', error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] p-4">
      <div className="max-w-md w-full space-y-6 text-center">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="flex justify-center"
        >
          <div className="p-4 bg-destructive/10 rounded-full">
            <AlertCircle className="w-12 h-12 text-destructive" />
          </div>
        </motion.div>

        <div className="space-y-2">
          <h2 className="text-xl font-bold">Application Error</h2>
          <p className="text-muted-foreground text-sm">
            {error.message || 'Something went wrong loading this page.'}
          </p>
        </div>

        {process.env.NODE_ENV === 'development' && error.digest && (
          <div className="p-3 bg-muted rounded-lg text-left">
            <p className="text-xs text-muted-foreground mb-1">Error digest:</p>
            <code className="text-xs font-mono">{error.digest}</code>
          </div>
        )}

        <div className="flex gap-3 justify-center">
          <Button onClick={reset} size="sm" className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Retry
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.history.back()}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Go back
          </Button>
        </div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
