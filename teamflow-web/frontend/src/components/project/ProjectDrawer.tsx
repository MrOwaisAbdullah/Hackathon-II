"use client";

/** ProjectDrawer - Side panel for editing project details.
 *
 * This component follows the exact same design pattern as TaskDrawer:
 * - Slides in from the right with spring animation
 * - Same styling, colors, animations as TaskDrawer
 * - Editable fields for name, description, status
 * - Save/Cancel actions with change detection
 */

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useUpdateProject } from "@/lib/query";
import { ProjectStatus } from "@/types";
import {
  Loader2,
  X,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RichTextEditor } from "@/components/task/RichTextEditor";

interface ProjectDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  project?: {
    id: string;
    name: string;
    description?: string;
    status: ProjectStatus;
    hourly_rate?: number;
    created_at?: string;
  };
}

export function ProjectDrawer({ isOpen, onClose, project }: ProjectDrawerProps) {
  const updateProject = useUpdateProject();

  // Local state for editing
  const [editedName, setEditedName] = useState("");
  const [editedDescription, setEditedDescription] = useState("");
  const [editedStatus, setEditedStatus] = useState<ProjectStatus | null>();
  const [editedHourlyRate, setEditedHourlyRate] = useState<number | undefined>();

  // Sync local state with project data whenever project changes
  useEffect(() => {
    if (project) {
      setEditedName(project.name);
      setEditedDescription(project.description || "");
      setEditedStatus(project.status);
      setEditedHourlyRate(project.hourly_rate);
    }
  }, [project]);

  const handleSave = async () => {
    if (!project) return;

    await updateProject.mutateAsync({
      id: project.id,
      data: {
        name: editedName,
        description: editedDescription || undefined,
        status: editedStatus || undefined,
        hourly_rate: editedHourlyRate ? Number(editedHourlyRate) : undefined,
      },
    });

    onClose();
  };

  const hasChanges = project && (
    editedName !== project.name ||
    editedDescription !== (project.description || "") ||
    editedStatus !== project.status ||
    editedHourlyRate !== project.hourly_rate
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-card shadow-xl z-50"
            data-testid="project-drawer"
          >
            <div className="flex h-full flex-col">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border p-4">
                <h2 className="text-lg font-semibold">Project Details</h2>
                <button
                  onClick={onClose}
                  className="rounded p-2 hover:bg-muted"
                  aria-label="Close drawer"
                  data-testid="close-drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-4 scrollbar-lime">
                {project ? (
                  <div className="space-y-6">
                    {/* Name - Editable */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Name
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={editedName}
                        onChange={(e) => setEditedName(e.target.value)}
                        className="w-full px-3 py-2 border-2 border-input rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent hover:border-input/80"
                        placeholder="Project name"
                      />
                    </div>

                    {/* Description - Rich Text Editor */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Description
                      </label>
                      <RichTextEditor
                        value={editedDescription}
                        onChange={setEditedDescription}
                        placeholder="Add a detailed description..."
                      />
                    </div>

                    {/* Status - Full Width (Editable) */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">
                        Status
                      </div>
                      <Select
                        value={editedStatus || ProjectStatus.ACTIVE}
                        onValueChange={(value) => setEditedStatus(value as ProjectStatus)}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value={ProjectStatus.ACTIVE}>Active</SelectItem>
                          <SelectItem value={ProjectStatus.ON_HOLD}>On Hold</SelectItem>
                          <SelectItem value={ProjectStatus.COMPLETED}>Completed</SelectItem>
                          <SelectItem value={ProjectStatus.ARCHIVED}>Archived</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Hourly Rate - Full Width (Editable) */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Hourly Rate ($)
                      </label>
                      <input
                        type="number"
                        value={editedHourlyRate || ''}
                        onChange={(e) => setEditedHourlyRate(e.target.value ? parseInt(e.target.value) : undefined)}
                        className="w-full px-3 py-2 border-2 border-input rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent hover:border-input/80"
                        placeholder="e.g. 50"
                        min="0"
                        step="1"
                      />
                      <p className="text-xs text-muted-foreground">
                        Required for profitability calculations (cost per hour)
                      </p>
                    </div>

                    {/* Created Date - Full Width (Read-only) */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">
                        Created
                      </div>
                      <div className="px-3 py-2 bg-muted/30 rounded-lg text-sm">
                        {project.created_at
                          ? new Date(project.created_at).toLocaleDateString(undefined, {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })
                          : "Recently"}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Select a project to view details
                  </p>
                )}
              </div>

              {/* Footer with Save Button */}
              {project && (
                <div className="flex items-center gap-3 p-4 border-t border-border">
                  <button
                    onClick={onClose}
                    className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    Cancel
                  </button>
                  <motion.button
                    whileHover={{ scale: hasChanges ? 1.01 : 1 }}
                    whileTap={{ scale: hasChanges ? 0.99 : 1 }}
                    onClick={handleSave}
                    disabled={!hasChanges || updateProject.isPending}
                    className={`
                      flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                      ${hasChanges
                        ? "bg-accent text-accent-foreground hover:bg-accent-hover"
                        : "bg-muted text-muted-foreground cursor-not-allowed"
                      }
                    `}
                  >
                    {updateProject.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                    ) : (
                      "Save Changes"
                    )}
                  </motion.button>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
