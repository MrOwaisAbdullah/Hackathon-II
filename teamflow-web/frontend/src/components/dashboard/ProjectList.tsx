'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MoreHorizontal, Calendar, ArrowRight, Edit, Trash2, ExternalLink, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUpdateProject, useDeleteProject } from '@/lib/query';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface Project {
  id: string;
  name: string;
  client: string;
  status: 'active' | 'completed' | 'on-hold';
  dueDate: string;
  progress: number;
}

interface ProjectListProps {
  projects: Project[];
  onEdit?: (project: Project) => void;
}

export function ProjectList({ projects, onEdit }: ProjectListProps) {
  const [isDark, setIsDark] = React.useState(false);
  const [showMenu, setShowMenu] = React.useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = React.useState<string | null>(null);

  const updateProject = useUpdateProject();
  const deleteProject = useDeleteProject();

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

  const getStatusStyle = (status: Project['status']) => {
    const styles = {
      active: {
        light: { backgroundColor: '#dcfce7', color: '#14532d' },
        dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
        icon: null, // No icon for active, just use the colored badge
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
    };
    return styles[status] || styles.on_hold;
  };

  const getStatusLabel = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'on_hold':
        return 'On Hold';
      case 'completed':
        return 'Completed';
      default:
        return status;
    }
  };

  // Date badge style - theme aware
  const dateBadgeStyle = {
    light: { backgroundColor: '#f3f4f6', color: '#6b7280' },
    dark: { backgroundColor: 'rgba(55, 65, 81, 0.5)', color: '#9ca3af' },
  };

  const finalDateStyle = isDark ? dateBadgeStyle.dark : dateBadgeStyle.light;

  // Handle status toggle
  const handleStatusToggle = async (project: Project) => {
    const newStatus = project.status === 'active' ? 'on-hold' : 'active';
    try {
      await updateProject.mutateAsync({
        id: project.id,
        data: { status: newStatus },
      });
      toast.success(`Project ${newStatus === 'active' ? 'activated' : 'put on hold'}`);
    } catch (error) {
      toast.error('Failed to update project status');
    }
    setShowMenu(null);
  };

  // Handle delete
  const handleDelete = async (projectId: string) => {
    try {
      await deleteProject.mutateAsync(projectId);
      toast.success('Project deleted successfully');
      setDeleteConfirm(null);
    } catch (error) {
      toast.error('Failed to delete project');
    }
    setShowMenu(null);
  };

  // Handle edit
  const handleEdit = (project: Project) => {
    onEdit?.(project);
    setShowMenu(null);
  };

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-base text-foreground tracking-tight uppercase">Active Projects</h3>
          <Link
            href="/projects"
            className="text-xs font-bold text-lime-600 dark:text-lime-400 hover:underline flex items-center gap-0.5 transition-colors"
          >
            View All <ArrowRight size={12} />
          </Link>
        </div>

        <div className="grid gap-3">
          {projects.map((project, index) => {
            const statusStyle = getStatusStyle(project.status);
            const finalStatusStyle = isDark ? statusStyle.dark : statusStyle.light;
            const statusIcon = statusStyle.icon;

            return (
              <motion.div
                key={project.id}
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

                <div className="relative">
                  {/* Header: Status Badge + Menu */}
                  <div className="flex items-center justify-between mb-3">
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
                    <DropdownMenu open={showMenu === project.id} onOpenChange={(open) => setShowMenu(open ? project.id : null)}>
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
                          asChild
                          className="cursor-pointer"
                        >
                          <Link href={`/projects/${project.id}`} className="flex items-center">
                            <ExternalLink className="w-4 h-4 mr-2 text-lime-600" />
                            <span>View Project</span>
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleEdit(project)}
                          className="cursor-pointer"
                        >
                          <Edit className="w-4 h-4 mr-2 text-lime-600" />
                          <span>Edit Project</span>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => handleStatusToggle(project)}
                          className="cursor-pointer"
                        >
                          {project.status === 'active' ? (
                            <>
                              <Calendar className="w-4 h-4 mr-2 text-amber-600" />
                              <span>Put On Hold</span>
                            </>
                          ) : (
                            <>
                              <Calendar className="w-4 h-4 mr-2 text-emerald-600" />
                              <span>Activate</span>
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => setDeleteConfirm(project.id)}
                          className="cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50 dark:focus:bg-rose-950/20"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          <span>Delete Project</span>
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  {/* Content */}
                  <Link href={`/projects/${project.id}`}>
                    <h4 className="font-bold text-sm mb-2 text-foreground leading-snug line-clamp-2 min-h-[2.5rem] group-hover:text-lime-600 dark:group-hover:text-lime-400 transition-colors">
                      {project.name}
                    </h4>
                    <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">{project.client}</p>
                  </Link>

                  {/* Footer: Progress + Date */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/60">
                    {/* Progress Bar */}
                    <div className="hidden sm:flex flex-col items-end gap-1 min-w-[120px]">
                      <div className="flex items-center gap-3 w-full">
                        <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${project.progress}%` }}
                            transition={{ duration: 1, delay: 0.5 + (index * 0.05) }}
                            className="h-full bg-lime-500 rounded-full"
                          />
                        </div>
                        <span className="text-[10px] font-bold w-8 text-right text-foreground tabular-nums">{project.progress}%</span>
                      </div>
                    </div>

                    {/* Date Badge */}
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="hidden sm:flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1.5 rounded-md"
                      style={finalDateStyle}
                    >
                      <Calendar size={14} strokeWidth={2} />
                      <span className="tabular-nums">{project.dueDate}</span>
                    </motion.div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {deleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setDeleteConfirm(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-card rounded-lg p-6 max-w-md w-full mx-4 border border-destructive/50 shadow-xl"
            >
              <h3 className="font-semibold text-lg mb-2">Delete Project?</h3>
              <p className="text-sm text-muted-foreground mb-6">
                This action cannot be undone. The project will be permanently deleted.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  disabled={deleteProject.isPending}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => deleteConfirm && handleDelete(deleteConfirm)}
                  disabled={deleteProject.isPending}
                  className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {deleteProject.isPending ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
