'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MoreHorizontal, Edit, Trash2, Calendar, CheckCircle } from 'lucide-react';
import type { Project, ProjectStatus } from '@/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface ProjectCardProps {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}

export function ProjectCard({ project, onEdit, onDelete }: ProjectCardProps) {
  const [showMenu, setShowMenu] = React.useState(false);
  const [isDark, setIsDark] = React.useState(false);

  // Detect dark mode
  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case 'active':
        return 'bg-lime-500';
      case 'on_hold':
        return 'bg-amber-500';
      case 'completed':
        return 'bg-emerald-500';
      case 'archived':
        return 'bg-zinc-400';
      default:
        return 'bg-zinc-400';
    }
  };

  const getStatusLabel = (status: ProjectStatus) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'on_hold':
        return 'On Hold';
      case 'completed':
        return 'Completed';
      case 'archived':
        return 'Archived';
      default:
        return status;
    }
  };

  // Status badge styles - theme aware
  const getStatusStyle = (status: ProjectStatus) => {
    const styles = {
      active: {
        light: { backgroundColor: '#dcfce7', color: '#14532d' },
        dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
        icon: 'spinner',
      },
      on_hold: {
        light: { backgroundColor: '#fef3c7', color: '#78350f' },
        dark: { backgroundColor: 'rgba(120, 53, 15, 0.3)', color: '#fbbf24' },
        icon: null,
      },
      completed: {
        light: { backgroundColor: '#dcfce7', color: '#14532d' },
        dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
        icon: CheckCircle,
      },
      archived: {
        light: { backgroundColor: '#f3f4f6', color: '#374151' },
        dark: { backgroundColor: 'rgba(55, 65, 81, 0.5)', color: '#9ca3af' },
        icon: null,
      },
    };
    return styles[status] || styles.archived;
  };

  const statusStyle = getStatusStyle(project.status);
  const finalStatusStyle = isDark ? statusStyle.dark : statusStyle.light;
  const statusIcon = statusStyle.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2, boxShadow: "0 8px 25px -5px rgba(0, 0, 0, 0.1)" }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-card p-4 shadow-sm",
        "transition-all duration-200 ease-out",
        "hover:shadow-lg hover:border-lime-500/30"
      )}
    >
      {/* Decorative gradient accent on hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-lime-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={false}
      />
      {/* Header: Status Badge + Menu */}
      <div className="flex items-center justify-between mb-3 relative">
        {/* Status Badge */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider"
          style={finalStatusStyle}
        >
          {statusIcon && typeof statusIcon !== "string" && (
            <statusIcon className="w-3 h-3" />
          )}
          {getStatusLabel(project.status)}
        </motion.div>

        {/* Actions Menu */}
        <DropdownMenu open={showMenu} onOpenChange={setShowMenu}>
          <DropdownMenuTrigger asChild>
            <motion.button
              whileHover={{ rotate: 90, scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200",
                "text-muted-foreground hover:text-foreground hover:bg-muted",
                "opacity-0 group-hover:opacity-100"
              )}
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal size={16} strokeWidth={2.5} />
            </motion.button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="end"
            className="w-48"
            sideOffset={5}
            onClick={(e) => e.stopPropagation()}
          >
            <DropdownMenuLabel className="text-xs font-semibold text-muted-foreground">
              Project Actions
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onEdit(project);
              }}
              className="cursor-pointer"
            >
              <Edit className="w-4 h-4 mr-2 text-lime-600" />
              <span>Edit Project</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDelete(project);
              }}
              className="cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50 dark:focus:bg-rose-950/20"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              <span>Delete Project</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Title */}
      <h3 className="font-bold text-base mb-2 text-foreground leading-snug line-clamp-2 min-h-[2.5rem] group-hover:text-lime-600 dark:group-hover:text-lime-400 transition-colors">
        {project.name}
      </h3>

      {/* Description */}
      {project.description && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-muted-foreground line-clamp-2 mb-3 leading-relaxed"
        >
          {project.description}
        </motion.p>
      )}

      {/* Footer: Created Date */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/60">
        {/* Created Date */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-1.5 text-[11px] text-muted-foreground font-medium"
        >
          <Calendar size={13} strokeWidth={2} className="text-lime-500" />
          <span>Created {new Date(project.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
        </motion.div>

        {/* Status Indicator Dot */}
        <motion.div
          whileHover={{ scale: 1.1 }}
          className={cn(
            "w-3 h-3 rounded-sm",
            getStatusColor(project.status)
          )}
        />
      </div>
    </motion.div>
  );
}
