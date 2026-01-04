"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, FolderOpen, Check } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Project {
  id: string;
  name: string;
  description?: string;
}

interface ProjectSelectProps {
  projects: Project[];
  value: string | null;
  onChange: (value: string | null) => void;
  label?: string;
  placeholder?: string;
  className?: string;
}

/**
 * ProjectSelect - Custom themed dropdown for project selection
 *
 * Provides consistent theming with the rest of the app,
 * replacing the native select element for better styling control.
 */
export function ProjectSelect({
  projects,
  value,
  onChange,
  label = "Project",
  placeholder = "No Project",
  className = "",
}: ProjectSelectProps) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedProject = projects.find((p) => p.id === value);

  return (
    <div className={cn("relative", className)}>
      {/* Label */}
      {label && (
        <label className="flex items-center gap-2 text-sm font-semibold text-foreground mb-2">
          <FolderOpen className="w-4 h-4 text-accent" />
          {label}
        </label>
      )}

      {/* Trigger Button */}
      <motion.button
        type="button"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 bg-background border-2 rounded-xl text-foreground cursor-pointer transition-all duration-200 hover:border-input/80 focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
            <FolderOpen className="w-4 h-4 text-accent" />
          </div>
          <span className="text-sm font-medium">
            {selectedProject?.name || placeholder}
          </span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />

            {/* Dropdown Menu */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 mt-2 w-full z-20"
            >
              <div className="bg-card border border-input rounded-xl shadow-lg overflow-hidden">
                <div className="p-1 max-h-60 overflow-y-auto">
                  {/* No Project Option */}
                  <button
                    type="button"
                    onClick={() => {
                      onChange(null);
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted/50 transition-colors text-left"
                  >
                    <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                      <span className="text-xs text-muted-foreground">—</span>
                    </div>
                    <span className="text-sm font-medium">{placeholder}</span>
                    {!value && (
                      <Check className="w-4 h-4 text-accent ml-auto" />
                    )}
                  </button>

                  {/* Projects */}
                  {projects.map((project) => (
                    <button
                      key={project.id}
                      type="button"
                      onClick={() => {
                        onChange(project.id);
                        setIsOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted/50 transition-colors text-left"
                    >
                      <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                        <FolderOpen className="w-4 h-4 text-accent" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium block truncate">
                          {project.name}
                        </span>
                        {project.description && (
                          <span className="text-xs text-muted-foreground truncate block">
                            {project.description}
                          </span>
                        )}
                      </div>
                      {value === project.id && (
                        <Check className="w-4 h-4 text-accent shrink-0" />
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
