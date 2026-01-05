'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Calendar, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import type { Task, TaskPriority } from '@/types';

interface DeadlineTask {
  id: string;
  title: string;
  dueDate: string;
  priority: TaskPriority;
  projectName: string;
  projectId: string;
  status: 'TODO' | 'DOING' | 'REVIEW';
  isOverdue: boolean;
  isDueSoon: boolean;
  daysUntilDue: number;
}

interface UpcomingDeadlinesProps {
  tasks?: Task[];
  projects?: { id: string; name: string }[];
}

// Date utilities
const getToday = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
};

const getDaysUntilDue = (dueDate: string): number => {
  const today = getToday();
  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);
  return Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};

// Process tasks into deadline items
const processDeadlines = (tasks: Task[], projects: { id: string; name: string }[]): DeadlineTask[] => {
  if (!tasks || tasks.length === 0) return [];

  const projectMap = new Map(projects.map(p => [p.id, p.name]));

  // Filter: exclude DONE/ARCHIVED, must have due_date
  const activeTasks = tasks.filter(
    task => task.due_date && task.status !== 'DONE' && task.status !== 'ARCHIVED'
  );

  // Process and add metadata
  const deadlineTasks: DeadlineTask[] = activeTasks.map(task => {
    const daysUntilDue = getDaysUntilDue(task.due_date!);
    const isOverdue = daysUntilDue < 0;
    const isDueSoon = daysUntilDue >= 0 && daysUntilDue <= 7;

    return {
      id: task.id,
      title: task.title,
      dueDate: task.due_date!,
      priority: task.priority,
      projectName: projectMap.get(task.project_id) || 'Unknown Project',
      projectId: task.project_id,
      status: task.status as 'TODO' | 'DOING' | 'REVIEW',
      isOverdue,
      isDueSoon,
      daysUntilDue,
    };
  });

  // Sort: overdue first (by most overdue), then upcoming (by due date)
  deadlineTasks.sort((a, b) => {
    if (a.isOverdue && b.isOverdue) {
      return a.daysUntilDue - b.daysUntilDue; // Most overdue first
    }
    if (a.isOverdue) return -1;
    if (b.isOverdue) return 1;
    return a.daysUntilDue - b.daysUntilDue;
  });

  // Limit to 8 tasks
  return deadlineTasks.slice(0, 8);
};

// Priority badge component
const PriorityBadge = ({ priority }: { priority: TaskPriority }) => {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const priorityStyles = {
    HIGH: {
      light: { backgroundColor: '#fef2f2', color: '#dc2626' },
      dark: { backgroundColor: 'rgba(220, 38, 38, 0.2)', color: '#f87171' },
    },
    MEDIUM: {
      light: { backgroundColor: '#fef3c7', color: '#d97706' },
      dark: { backgroundColor: 'rgba(217, 119, 6, 0.2)', color: '#fbbf24' },
    },
    LOW: {
      light: { backgroundColor: '#f1f5f9', color: '#64748b' },
      dark: { backgroundColor: 'rgba(100, 116, 139, 0.2)', color: '#94a3b8' },
    },
  };

  const styles = priorityStyles[priority];
  const finalStyle = isDark ? styles.dark : styles.light;

  return (
    <span
      className="text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider"
      style={finalStyle}
    >
      {priority}
    </span>
  );
};

// Deadline badge component
const DeadlineBadge = ({ task }: { task: DeadlineTask }) => {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  if (task.isOverdue) {
    const overdueStyle = {
      light: { backgroundColor: '#fef2f2', color: '#dc2626' },
      dark: { backgroundColor: 'rgba(220, 38, 38, 0.2)', color: '#f87171' },
    };
    const finalStyle = isDark ? overdueStyle.dark : overdueStyle.light;

    return (
      <span
        className="text-[10px] font-bold px-2 py-0.5 rounded-sm flex items-center gap-1"
        style={finalStyle}
      >
        <AlertCircle size={10} />
        Overdue by {Math.abs(task.daysUntilDue)}d
      </span>
    );
  }

  if (task.isDueSoon && task.daysUntilDue <= 3) {
    const dueSoonStyle = {
      light: { backgroundColor: '#fef3c7', color: '#d97706' },
      dark: { backgroundColor: 'rgba(217, 119, 6, 0.2)', color: '#fbbf24' },
    };
    const finalStyle = isDark ? dueSoonStyle.dark : dueSoonStyle.light;

    return (
      <span
        className="text-[10px] font-semibold px-2 py-0.5 rounded-sm"
        style={finalStyle}
      >
        Due in {task.daysUntilDue}d
      </span>
    );
  }

  return null;
};

// Individual deadline item
const DeadlineItem = ({ task, index }: { task: DeadlineTask; index: number }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: 0.2 + (index * 0.05) }}
      whileHover={{ x: 2 }}
      className="group"
    >
      <Link href={`/projects/${task.projectId}`}>
        <motion.div
          className="flex items-start gap-3 p-2.5 rounded-lg border border-transparent hover:border-border/50 transition-all duration-200"
          whileHover={{ backgroundColor: 'hsl(var(--muted) / 0.5)' }}
        >
          {/* Priority Icon */}
          <div className="relative mt-0.5">
            <motion.div
              animate={
                task.isOverdue
                  ? { scale: [1, 1.1, 1] }
                  : { scale: 1 }
              }
              transition={
                task.isOverdue
                  ? { repeat: Infinity, duration: 2, ease: 'easeInOut' }
                  : {}
              }
            >
              <AlertCircle
                size={16}
                className={
                  task.isOverdue
                    ? 'text-destructive'
                    : task.priority === 'HIGH'
                      ? 'text-destructive/70'
                      : task.priority === 'MEDIUM'
                        ? 'text-amber-500'
                        : 'text-muted-foreground/50'
                }
                strokeWidth={2.5}
              />
            </motion.div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-foreground leading-snug line-clamp-2 group-hover:text-accent transition-colors">
                  {task.title}
                </h4>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  <span className="text-xs text-muted-foreground truncate max-w-[150px]">
                    {task.projectName}
                  </span>
                  <PriorityBadge priority={task.priority} />
                </div>
              </div>

              {/* Due Date Badge */}
              <div className="flex flex-col items-end gap-1">
                <DeadlineBadge task={task} />
                <span className="text-[10px] font-mono text-muted-foreground tabular-nums">
                  {formatDate(task.dueDate)}
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </Link>
    </motion.div>
  );
};

// Empty state component
const EmptyState = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay: 0.3 }}
    className="text-center py-10"
  >
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
    >
      <Calendar className="w-12 h-12 mx-auto text-muted-foreground/20 mb-4" />
    </motion.div>
    <p className="text-sm text-muted-foreground font-medium">No upcoming deadlines</p>
    <p className="text-xs text-muted-foreground/60 mt-1.5 max-w-[180px] mx-auto">
      Tasks with due dates will appear here
    </p>
  </motion.div>
);

// Main component
export function UpcomingDeadlines({ tasks = [], projects = [] }: UpcomingDeadlinesProps) {
  const deadlines = processDeadlines(tasks, projects);
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.15, ease: 'easeOut' }}
      className="card-float p-6 rounded-lg h-full flex flex-col"
    >
      {/* Header */}
      <div className="mb-5 border-b border-border pb-4 flex items-center justify-between">
        <div>
          <h3 className="font-bold text-base text-foreground tracking-tight uppercase">
            Upcoming Deadlines
          </h3>
          {deadlines.length > 0 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-xs text-muted-foreground mt-1"
            >
              {deadlines.filter(d => d.isOverdue).length} overdue · {deadlines.filter(d => !d.isOverdue && d.isDueSoon).length} due soon
            </motion.p>
          )}
        </div>
        {deadlines.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, type: 'spring', stiffness: 200 }}
            className="h-8 w-8 rounded-full bg-accent/10 flex items-center justify-center"
          >
            <span className="text-xs font-bold text-accent">{deadlines.length}</span>
          </motion.div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1">
        <AnimatePresence mode="wait">
          {deadlines.length === 0 ? (
            <EmptyState key="empty" />
          ) : (
            <motion.div
              key="list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-2"
            >
              {deadlines.map((task, index) => (
                <DeadlineItem key={task.id} task={task} index={index} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Link */}
      {deadlines.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="pt-4 mt-4 border-t border-border"
        >
          <Link
            href="/tasks"
            className="flex items-center justify-center gap-2 text-xs font-semibold text-accent hover:underline transition-all"
          >
            View all tasks
            <ArrowRight size={14} />
          </Link>
        </motion.div>
      )}
    </motion.div>
  );
}
