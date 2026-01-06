
'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { motion } from 'framer-motion';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      // Updated: Slightly lighter background for visibility in dark sidebar
      className="relative p-2 rounded-full bg-zinc-800/80 hover:bg-zinc-700 transition-colors border border-zinc-700 ring-1 ring-white/5"
      aria-label="Toggle theme"
    >
      <div className="relative w-4 h-4">
        <motion.div
          initial={false}
          animate={{
            scale: theme === 'dark' ? 0 : 1,
            opacity: theme === 'dark' ? 0 : 1,
            rotate: theme === 'dark' ? -90 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {/* Sun icon for Light Mode - Visible against dark sidebar */}
          <Sun className="w-4 h-4 text-yellow-400" />
        </motion.div>
        
        <motion.div
          initial={false}
          animate={{
            scale: theme === 'dark' ? 1 : 0,
            opacity: theme === 'dark' ? 1 : 0,
            rotate: theme === 'dark' ? 0 : 90,
          }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {/* Moon icon for Dark Mode - Visible against dark sidebar */}
          <Moon className="w-4 h-4 text-lime-400" />
        </motion.div>
      </div>
    </motion.button>
  );
}
