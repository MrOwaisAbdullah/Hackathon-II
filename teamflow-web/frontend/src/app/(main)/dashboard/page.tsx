"use client";

/** Projects page - Grid view of all projects.
 *
 * Features:
 * - Grid layout of project cards
 * - Project status indicators
 * - Task count display
 * - Create new project button
 * - Mock data (will be replaced with API calls)
 */

import { motion } from "framer-motion";
import Link from "next/link";
import type { Project, ProjectStatus } from "@/types";

// Mock data - will be replaced with API calls
const mockProjects: Project[] = [
  {
    id: "proj-1",
    name: "Website Redesign",
    description: "Complete redesign of the company website with modern UI/UX",
    agency_id: "agency-1",
    status: "active" as ProjectStatus,
    created_at: new Date().toISOString(),
    updated_at: null,
  },
  {
    id: "proj-2",
    name: "Mobile App Development",
    description: "Native iOS and Android app for customer engagement",
    agency_id: "agency-1",
    status: "active" as ProjectStatus,
    created_at: new Date().toISOString(),
    updated_at: null,
  },
  {
    id: "proj-3",
    name: "Marketing Campaign",
    description: "Q1 digital marketing campaign and social media strategy",
    agency_id: "agency-1",
    status: "active" as ProjectStatus,
    created_at: new Date().toISOString(),
    updated_at: null,
  },
  {
    id: "proj-4",
    name: "Brand Identity",
    description: "Logo design and brand guidelines for startup client",
    agency_id: "agency-1",
    status: "archived" as ProjectStatus,
    created_at: new Date().toISOString(),
    updated_at: null,
  },
];

// Mock task counts
const mockTaskCounts: Record<string, { total: number; completed: number }> = {
  "proj-1": { total: 24, completed: 16 },
  "proj-2": { total: 18, completed: 8 },
  "proj-3": { total: 12, completed: 3 },
  "proj-4": { total: 30, completed: 30 },
};

const statusConfig: Record<ProjectStatus, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-500" },
  archived: { label: "Archived", color: "bg-gray-400" },
};

export default function ProjectsPage() {
  const activeProjects = mockProjects.filter((p) => p.status === "active");
  const archivedProjects = mockProjects.filter((p) => p.status === "archived");

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Projects</h1>
          <p className="text-muted-foreground mt-1">
            Manage your agency's projects
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
        >
          New Project
        </motion.button>
      </div>

      {/* Active Projects */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-foreground mb-4">
          Active Projects ({activeProjects.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeProjects.map((project, index) => (
            <ProjectCard
              key={project.id}
              project={project}
              taskCount={mockTaskCounts[project.id] || { total: 0, completed: 0 }}
              index={index}
            />
          ))}
        </div>
      </div>

      {/* Archived Projects */}
      {archivedProjects.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Archived Projects ({archivedProjects.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {archivedProjects.map((project, index) => (
              <ProjectCard
                key={project.id}
                project={project}
                taskCount={mockTaskCounts[project.id] || { total: 0, completed: 0 }}
                index={index}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface ProjectCardProps {
  project: Project;
  taskCount: { total: number; completed: number };
  index: number;
}

function ProjectCard({ project, taskCount, index }: ProjectCardProps) {
  const statusInfo = statusConfig[project.status];
  const progress = taskCount.total > 0 ? (taskCount.completed / taskCount.total) * 100 : 0;

  return (
    <Link href={`/projects/${project.id}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.05 }}
        whileHover={{ y: -4, boxShadow: "0 10px 40px rgba(0,0,0,0.1)" }}
        className="bg-card rounded-lg p-6 border border-border cursor-pointer"
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-foreground line-clamp-1">
            {project.name}
          </h3>
          <div className={`w-2 h-2 rounded-full ${statusInfo.color} flex-shrink-0 ml-2`} />
        </div>

        {/* Description */}
        {project.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {project.description}
          </p>
        )}

        {/* Progress */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-foreground font-medium">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="bg-primary h-2 rounded-full"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {taskCount.completed} of {taskCount.total} tasks
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            project.status === "active" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
          }`}>
            {statusInfo.label}
          </span>
        </div>
      </motion.div>
    </Link>
  );
}
