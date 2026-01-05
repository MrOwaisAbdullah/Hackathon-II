"use client";

import { useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, Calendar, Building2, CheckCircle, Clock, Users } from "lucide-react";
import { useProject, useTasks } from "@/lib/query";
import { ProjectStatus } from "@/types";
import { cn } from "@/lib/utils";

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const router = useRouter();
  const { id } = use(params);
  const { data: project, isLoading, error } = useProject(id);
  const { data: tasks = [] } = useTasks();

  // Filter tasks for this project
  const projectTasks = tasks.filter((task) => task.project_id === id);
  const completedTasks = projectTasks.filter((t) => t.status === "DONE").length;
  const progress = projectTasks.length > 0
    ? Math.round((completedTasks / projectTasks.length) * 100)
    : 0;

  useEffect(() => {
    if (error) {
      router.push("/projects");
    }
  }, [error, router]);

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-accent" />
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-8">
        <div className="text-center py-20">
          <p className="text-muted-foreground">Project not found</p>
        </div>
      </div>
    );
  }

  const getStatusStyle = (status: ProjectStatus) => {
    const styles = {
      active: {
        bg: "bg-emerald-500/10 dark:bg-emerald-500/20",
        text: "text-emerald-700 dark:text-emerald-400",
        border: "border-emerald-200 dark:border-emerald-800",
      },
      on_hold: {
        bg: "bg-amber-500/10 dark:bg-amber-500/20",
        text: "text-amber-700 dark:text-amber-400",
        border: "border-amber-200 dark:border-amber-800",
      },
      completed: {
        bg: "bg-blue-500/10 dark:bg-blue-500/20",
        text: "text-blue-700 dark:text-blue-400",
        border: "border-blue-200 dark:border-blue-800",
      },
      archived: {
        bg: "bg-gray-500/10 dark:bg-gray-500/20",
        text: "text-gray-700 dark:text-gray-400",
        border: "border-gray-200 dark:border-gray-800",
      },
    };
    return styles[status] || styles.active;
  };

  const getStatusLabel = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.ACTIVE:
        return "Active";
      case ProjectStatus.ON_HOLD:
        return "On Hold";
      case ProjectStatus.COMPLETED:
        return "Completed";
      case ProjectStatus.ARCHIVED:
        return "Archived";
      default:
        return status;
    }
  };

  const statusStyle = getStatusStyle(project.status);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Back Button */}
      <motion.button
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => router.back()}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
      >
        <ArrowLeft size={20} />
        <span>Back to Projects</span>
      </motion.button>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">{project.name}</h1>
            <div className="flex items-center gap-4">
              {/* Status Badge */}
              <span
                className={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border",
                  statusStyle.bg,
                  statusStyle.text,
                  statusStyle.border
                )}
              >
                {project.status === ProjectStatus.COMPLETED && (
                  <CheckCircle size={14} />
                )}
                {getStatusLabel(project.status)}
              </span>

              {/* Created Date */}
              <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <Calendar size={14} />
                Created {new Date(project.created_at).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Description */}
      {project.description && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="bg-muted/30 rounded-xl p-6 border border-border">
            <h2 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
              <Building2 size={16} />
              Description
            </h2>
            <p className="text-foreground leading-relaxed">{project.description}</p>
          </div>
        </motion.div>
      )}

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
      >
        {/* Total Tasks */}
        <div className="bg-card rounded-xl p-6 border border-border">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="text-2xl font-bold">{projectTasks.length}</p>
              <p className="text-sm text-muted-foreground">Total Tasks</p>
            </div>
          </div>
        </div>

        {/* Completed */}
        <div className="bg-card rounded-xl p-6 border border-border">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{completedTasks}</p>
              <p className="text-sm text-muted-foreground">Completed</p>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="bg-card rounded-xl p-6 border border-border">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Clock className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{progress}%</p>
              <p className="text-sm text-muted-foreground">Progress</p>
            </div>
          </div>
          {/* Progress Bar */}
          <div className="w-full h-2 bg-secondary rounded-full overflow-hidden mt-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className="h-full bg-accent rounded-full"
            />
          </div>
        </div>
      </motion.div>

      {/* Tasks Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5" />
          Project Tasks
        </h2>
        {projectTasks.length === 0 ? (
          <div className="text-center py-12 bg-muted/20 rounded-xl border border-border">
            <p className="text-muted-foreground">No tasks in this project yet</p>
          </div>
        ) : (
          <div className="bg-card rounded-xl border border-border divide-y divide-border">
            {projectTasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.05 }}
                className="p-4 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-foreground mb-1">{task.title}</h3>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>{task.status}</span>
                      {task.due_date && (
                        <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "px-2 py-1 rounded text-xs font-medium",
                        task.priority === "HIGH" && "bg-red-500/10 text-red-500",
                        task.priority === "MEDIUM" && "bg-amber-500/10 text-amber-500",
                        task.priority === "LOW" && "bg-blue-500/10 text-blue-500"
                      )}
                    >
                      {task.priority}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
