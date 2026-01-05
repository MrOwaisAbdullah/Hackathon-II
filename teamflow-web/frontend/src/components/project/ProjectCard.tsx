'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MoreHorizontal, Edit, Trash2, Calendar, CheckCircle, ExternalLink, FolderOpen } from 'lucide-react';
import Link from 'next/link';
import type { Project, ProjectStatus } from '@/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { useUpdateProject } from '@/lib/query';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { renderMarkdown } from '@/lib/markdown';

interface ProjectCardProps {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}

export function ProjectCard({ project, onEdit, onDelete }: ProjectCardProps) {
  const [showMenu, setShowMenu] = React.useState(false);
  const [isDark, setIsDark] = React.useState(false);
  const updateProject = useUpdateProject();

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

  // Handle status toggle
  const handleStatusToggle = async () => {
    const newStatus = project.status === 'active' ? 'on_hold' : 'active';
    try {
      await updateProject.mutateAsync({
        id: project.id,
        data: { status: newStatus },
      });
      toast.success(`Project ${newStatus === 'active' ? 'activated' : 'put on hold'}`);
    } catch (error) {
      toast.error('Failed to update project status');
    }
    setShowMenu(false);
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
        "group relative overflow-hidden rounded-xl border bg-card p-3 md:p-4 shadow-sm w-full min-w-0",
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
              className="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 text-muted-foreground hover:text-foreground hover:bg-muted"
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
              asChild
              className="cursor-pointer"
            >
              <Link href={`/projects/${project.id}`} className="flex items-center">
                <ExternalLink className="w-4 h-4 mr-2 text-accent" />
                <span>View Project</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onEdit(project);
              }}
              className="cursor-pointer"
            >
              <Edit className="w-4 h-4 mr-2 text-accent" />
              <span>Edit Project</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {/* Status Toggle - only show for active/on_hold projects */}
            {(project.status === 'active' || project.status === 'on_hold') && (
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  handleStatusToggle();
                }}
                className="cursor-pointer"
              >
                {project.status === 'active' ? (
                  <>
                    <Calendar className="w-4 h-4 mr-2 text-amber-600" />
                    <span>Put On Hold</span>
                  </>
                ) : (
                  <>
                    <FolderOpen className="w-4 h-4 mr-2 text-emerald-600" />
                    <span>Activate</span>
                  </>
                )}
              </DropdownMenuItem>
            )}
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDelete(project);
              }}
              className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              <span>Delete Project</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Title */}
      <Link href={`/projects/${project.id}`}>
        <h3 className="font-bold text-base mb-2 text-foreground leading-snug line-clamp-2 min-h-[2.5rem] group-hover:text-accent transition-colors">
          {project.name}
        </h3>
      </Link>

      {/* Description - T623: Mobile line-clamp-2, w-full for overflow prevention */}
      {project.description && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-muted-foreground line-clamp-2 mb-3 leading-relaxed prose prose-xs max-w-none dark:prose-invert w-full"
          dangerouslySetInnerHTML={{
            __html: renderMarkdown(project.description)
          }}
        />
      )}

      {/* Footer: Created Date */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/60">
        {/* Created Date */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-1.5 text-[11px] text-muted-foreground font-medium"
        >
          <Calendar size={13} strokeWidth={2} className="text-accent" />
          <span>Created {new Date(project.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
        </motion.div>

        {/* Status Indicator Dot - using theme-aware colors */}
        <motion.div
          whileHover={{ scale: 1.1 }}
          className={cn(
            "w-3 h-3 rounded-sm",
            project.status === 'active' && "bg-accent",
            project.status === 'on_hold' && "bg-amber-500",
            project.status === 'completed' && "bg-emerald-500",
            project.status === 'archived' && "bg-muted-foreground"
          )}
        />
      </div>
    </motion.div>
  );
}
