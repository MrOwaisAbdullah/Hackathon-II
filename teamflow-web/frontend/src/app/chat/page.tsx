'use client';

/**
 * Fullscreen Chat Page - T097
 *
 * This page provides a dedicated fullscreen chat interface similar to ChatGPT.
 * Located outside (main) route group to avoid layout conflicts.
 *
 * Users can access this page via:
 * - Sidebar "AI Assistant" button (T097a)
 * - Direct navigation to /chat
 * - Keyboard shortcut from anywhere in the app
 *
 * Theme Support:
 * - Respects application theme (light/dark mode)
 * - Theme toggle button in status bar
 * - Uses application CSS variables for consistent styling
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useState, useEffect } from 'react';
import { ArrowLeft, Moon, Sun, Minimize2 } from 'lucide-react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useTheme } from '@/contexts/ThemeContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function ChatPageContent() {
  const [error, setError] = useState<string | null>(null);
  const { theme, toggleTheme } = useTheme();

  // Resolve 'system' theme to actual 'light' or 'dark' for ChatKit
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      setResolvedTheme(systemTheme);
    } else {
      setResolvedTheme(theme as 'light' | 'dark');
    }
  }, [theme]);

  // ChatKit setup
  const { control, ref } = useChatKit({
    api: {
      url: `${API_URL}/api/v1/chat/chatkit`,
      domainKey: 'local-dev',
    },
    theme: resolvedTheme,
    startScreen: {
      greeting: 'Hello! I\'m TeamFlow AI. How can I help you today?',
      prompts: [
        {
          label: 'Ask about project docs',
          prompt: 'What are the design requirements for the landing page?',
          icon: 'document',
        },
        {
          label: 'Team management',
          prompt: 'Who is available for new tasks?',
          icon: 'profile',
        },
        {
          label: 'Project help',
          prompt: 'How do we handle authentication errors?',
          icon: 'circle-question',
        },
        {
          label: 'Create a task',
          prompt: 'Create a task for the landing page redesign',
          icon: 'plus',
        },
      ],
    },
    threadItemActions: {
      feedback: true,
      retry: false,
    },
    onReady: () => {
      console.log('[ChatPage] ChatKit ready')
    },
    onError: ({ error }: { error: any }) => {
      console.error('[ChatPage] ChatKit error:', error)
      setError(error.message)
    },
  });

  return (
    <div className="h-screen w-screen flex flex-col bg-background">
      {/* Header with back button and theme toggle */}
      <div className="flex items-center px-4 py-3 bg-muted border-b border-border">
        <Link
          href="/dashboard"
          className="flex items-center text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </Link>
        <h1 className="ml-6 text-lg font-semibold text-foreground">TeamFlow AI Assistant</h1>

        <div className="ml-auto flex items-center space-x-2">
          {/* Theme toggle button */}
          <button
            onClick={toggleTheme}
            className="text-muted-foreground hover:text-foreground p-2 rounded-lg hover:bg-secondary transition-colors"
            aria-label={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
            title={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
          >
            {resolvedTheme === 'light' ? (
              <Moon className="h-5 w-5" strokeWidth={1.5} />
            ) : (
              <Sun className="h-5 w-5" strokeWidth={1.5} />
            )}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="fixed top-20 right-4 z-[10000] max-w-sm rounded-lg bg-destructive/10 border border-destructive/20 p-4 shadow-lg">
          <div className="flex items-start">
            <p className="text-sm text-destructive">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-destructive hover:text-destructive/80"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main ChatKit - fills available space */}
      <div className="flex-1 overflow-hidden">
        <ChatKit
          control={control}
          ref={ref}
          className="h-full w-full"
        />
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}
