'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

/**
 * T154: Global Error Boundary for the application
 *
 * This error boundary catches all errors in the application
 * and displays a user-friendly error message.
 *
 * Note: error.tsx files must be Client Components.
 */

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service in production
    console.error('Global error caught:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-background">
      <div className="max-w-md w-full space-y-6 text-center">
        {/* Error Icon */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="flex justify-center"
        >
          <div className="p-4 bg-destructive/10 rounded-full">
            <AlertCircle className="w-16 h-16 text-destructive" />
          </div>
        </motion.div>

        {/* Error Message */}
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Something went wrong</h1>
          <p className="text-muted-foreground">
            {error.message || 'An unexpected error occurred. Please try again.'}
          </p>
        </div>

        {/* Error Details (development only) */}
        {process.env.NODE_ENV === 'development' && error.digest && (
          <div className="p-3 bg-muted rounded-lg text-left">
            <p className="text-xs text-muted-foreground mb-1">Error ID:</p>
            <code className="text-xs font-mono">{error.digest}</code>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            onClick={reset}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Try again
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Go to home
          </Button>
        </div>

        {/* Support Link */}
        <p className="text-sm text-muted-foreground">
          If this problem persists, please{' '}
          <a href="mailto:support@teamflow.dev" className="text-primary hover:underline">
            contact support
          </a>
        </p>
      </div>
    </div>
  );
}

// Import motion for the animation
import { motion } from 'framer-motion';
