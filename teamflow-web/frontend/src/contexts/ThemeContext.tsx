/** Theme provider context with support for light/dark mode. */
'use client';

import { useEffect, useState } from 'react';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mounted, setMounted] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Only run on client
  useEffect(() => {
    setMounted(true);

    // Get theme from localStorage
    const storedTheme = localStorage.getItem('teamflow-ui-storage');
    if (storedTheme) {
      try {
        const parsed = JSON.parse(storedTheme);
        const themeValue = parsed?.state?.theme;
        if (themeValue) {
          setTheme(themeValue);
          document.documentElement.classList.add(themeValue);
        }
      } catch (e) {
        // Use default
        document.documentElement.classList.add('light');
      }
    }
  }, []);

  // Don't render anything until mounted to prevent SSR mismatch
  if (!mounted) {
    return <>{children}</>;
  }

  return <>{children}</>;
}
