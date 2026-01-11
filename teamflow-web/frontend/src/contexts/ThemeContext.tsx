'use client';

import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';

type Theme = 'dark' | 'light' | 'system';

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

interface ThemeProviderState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const initialState: ThemeProviderState = {
  theme: 'light',
  setTheme: () => null,
  toggleTheme: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = 'light',
  storageKey = 'theme',
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check if running on client
    if (typeof window !== 'undefined') {
      // Clear old 'vite-ui-theme' key to avoid conflicts
      localStorage.removeItem('vite-ui-theme')

      const savedTheme = localStorage.getItem(storageKey) as Theme | null

      // If saved theme is 'system', default to 'light' for consistency
      if (savedTheme === 'system' || !savedTheme) {
        return defaultTheme
      }

      return savedTheme
    }
    return defaultTheme
  });

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches
        ? 'dark'
        : 'light';

      root.classList.add(systemTheme);
      return;
    }

    root.classList.add(theme);
  }, [theme]);

  const value = useMemo(() => ({
    theme,
    setTheme: (newTheme: Theme) => {
      console.log('[ThemeContext] setTheme called with:', newTheme)
      localStorage.setItem(storageKey, newTheme);
      setTheme(newTheme);
    },
    toggleTheme: () => {
      setTheme(prev => {
        const newTheme = prev === 'light' ? 'dark' : 'light';
        console.log('[ThemeContext] Toggling from', prev, 'to', newTheme);
        return newTheme;
      });
    },
  }), [theme, storageKey]);

  return (
    <ThemeProviderContext.Provider value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error('useTheme must be used within a ThemeProvider');

  return context;
};