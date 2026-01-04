'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  LayoutDashboard,
  CheckSquare,
  FolderKanban,
  Users,
  Clock,
  Settings,
  LogOut,
  Sun,
  Moon,
  Archive,
  Plus,
  Command as CommandIcon,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/hooks/useAuth';

interface Command {
  id: string;
  label: string;
  description?: string;
  icon: React.ElementType;
  action: () => void;
  category: 'navigation' | 'actions' | 'settings';
  shortcut?: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  navigation: 'Navigation',
  actions: 'Actions',
  settings: 'Settings',
};

export function CommandPalette() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { logout } = useAuth();
  const searchInputRef = React.useRef<HTMLInputElement>(null);
  const listRef = React.useRef<HTMLDivElement>(null);

  // Resolve current theme for display (handle 'system' theme)
  const resolvedTheme = React.useMemo(() => {
    if (theme === 'system') {
      return typeof window !== 'undefined' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    }
    return theme;
  }, [theme]);

  // Define all available commands
  const commands: Command[] = [
    // Navigation
    {
      id: 'nav-dashboard',
      label: 'Go to Dashboard',
      description: 'View your agency overview and metrics',
      icon: LayoutDashboard,
      action: () => router.push('/dashboard'),
      category: 'navigation',
    },
    {
      id: 'nav-tasks',
      label: 'Go to Tasks',
      description: 'View and manage your task board',
      icon: CheckSquare,
      action: () => router.push('/tasks'),
      category: 'navigation',
    },
    {
      id: 'nav-projects',
      label: 'Go to Projects',
      description: 'View all your projects',
      icon: FolderKanban,
      action: () => router.push('/projects'),
      category: 'navigation',
    },
    {
      id: 'nav-team',
      label: 'Go to Team',
      description: 'Manage your team members',
      icon: Users,
      action: () => router.push('/team'),
      category: 'navigation',
    },
    {
      id: 'nav-time',
      label: 'Go to Time Entries',
      description: 'View your logged time entries',
      icon: Clock,
      action: () => router.push('/time-entries'),
      category: 'navigation',
    },
    {
      id: 'nav-archive',
      label: 'Go to Archive',
      description: 'View archived tasks',
      icon: Archive,
      action: () => router.push('/archive'),
      category: 'navigation',
    },
    {
      id: 'nav-settings',
      label: 'Go to Settings',
      description: 'Manage your account settings',
      icon: Settings,
      action: () => router.push('/settings'),
      category: 'navigation',
    },
    // Actions
    {
      id: 'action-new-task',
      label: 'Create New Task',
      description: 'Quickly create a new task',
      icon: Plus,
      action: () => {
        router.push('/tasks');
        // Could trigger task form modal in future
      },
      category: 'actions',
      shortcut: 'N',
    },
    {
      id: 'action-logout',
      label: 'Logout',
      description: 'Sign out of your account',
      icon: LogOut,
      action: () => logout(),
      category: 'actions',
    },
    // Settings
    {
      id: 'theme-toggle',
      label: 'Toggle Theme',
      description: resolvedTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode',
      icon: resolvedTheme === 'dark' ? Sun : Moon,
      action: () => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark'),
      category: 'settings',
    },
  ];

  // Filter commands based on search query
  const filteredCommands = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return commands;
    }
    const query = searchQuery.toLowerCase();
    return commands.filter(
      (cmd) =>
        cmd.label.toLowerCase().includes(query) ||
        cmd.description?.toLowerCase().includes(query) ||
        cmd.category.toLowerCase().includes(query)
    );
  }, [searchQuery, commands]);

  // Group filtered commands by category
  const groupedCommands = React.useMemo(() => {
    const groups: Record<string, Command[]> = {};
    filteredCommands.forEach((cmd) => {
      if (!groups[cmd.category]) {
        groups[cmd.category] = [];
      }
      groups[cmd.category].push(cmd);
    });
    return groups;
  }, [filteredCommands]);

  // Flatten commands for keyboard navigation
  const flatCommands = React.useMemo(() => {
    return Object.values(groupedCommands).flat();
  }, [groupedCommands]);

  // Reset selected index when filtered commands change
  React.useEffect(() => {
    setSelectedIndex(0);
  }, [filteredCommands]);

  // Keyboard shortcut: CMD+K or Ctrl+K
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // CMD+K or Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        setSearchQuery('');
      }
      // ESC to close
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Focus search input when opening
  React.useEffect(() => {
    if (isOpen) {
      searchInputRef.current?.focus();
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Keyboard navigation within command palette
  const handleListKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % flatCommands.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + flatCommands.length) % flatCommands.length);
        break;
      case 'Enter':
        e.preventDefault();
        if (flatCommands[selectedIndex]) {
          flatCommands[selectedIndex].action();
          setIsOpen(false);
        }
        break;
    }
  };

  // Execute command and close palette
  const executeCommand = (command: Command) => {
    command.action();
    setIsOpen(false);
    setSearchQuery('');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50"
            onClick={() => setIsOpen(false)}
          />

          {/* Command Palette Modal */}
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
            <motion.div
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-2xl mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="bg-card border border-border rounded-lg shadow-2xl overflow-hidden">
                {/* Search Input */}
                <div className="flex items-center gap-3 px-4 py-4 border-b border-border">
                  <Search className="w-5 h-5 text-muted-foreground shrink-0" />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleListKeyDown}
                    placeholder="Type a command or search..."
                    className="flex-1 bg-transparent border-none outline-none text-base placeholder:text-muted-foreground"
                  />
                  <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-muted-foreground bg-muted rounded">
                    <span>ESC</span>
                  </kbd>
                </div>

                {/* Command List */}
                <div
                  ref={listRef}
                  className="max-h-[400px] overflow-y-auto py-2"
                  onKeyDown={handleListKeyDown}
                >
                  {flatCommands.length === 0 ? (
                    <div className="px-4 py-8 text-center text-muted-foreground">
                      No commands found
                    </div>
                  ) : (
                    Object.entries(groupedCommands).map(([category, cmds]) => (
                      <div key={category} className="mb-2">
                        {/* Category Header */}
                        <div className="px-4 py-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                          {CATEGORY_LABELS[category] || category}
                        </div>

                        {/* Commands in this category */}
                        {cmds.map((command) => {
                          const globalIndex = flatCommands.indexOf(command);
                          const isSelected = globalIndex === selectedIndex;
                          const Icon = command.icon;

                          return (
                            <motion.button
                              key={command.id}
                              type="button"
                              onClick={() => executeCommand(command)}
                              className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                                isSelected
                                  ? 'bg-accent text-accent-foreground'
                                  : 'hover:bg-muted hover:text-foreground'
                              }`}
                              initial={false}
                              animate={{
                                backgroundColor: isSelected ? 'hsl(var(--accent))' : 'transparent',
                              }}
                              transition={{ duration: 0.15 }}
                            >
                              <div className="shrink-0">
                                <Icon className="w-5 h-5" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium truncate">{command.label}</div>
                                {command.description && (
                                  <div className="text-sm text-muted-foreground truncate">
                                    {command.description}
                                  </div>
                                )}
                              </div>
                              {command.shortcut && (
                                <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-muted-foreground bg-muted rounded">
                                  {command.shortcut}
                                </kbd>
                              )}
                            </motion.button>
                          );
                        })}
                      </div>
                    ))
                  )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-2 border-t border-border text-xs text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <kbd className="px-1.5 py-0.5 bg-muted rounded">↑↓</kbd>
                      <span>to navigate</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <kbd className="px-1.5 py-0.5 bg-muted rounded">↵</kbd>
                      <span>to select</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <CommandIcon className="w-3 h-3" />
                    <kbd className="px-1.5 py-0.5 bg-muted rounded">K</kbd>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
