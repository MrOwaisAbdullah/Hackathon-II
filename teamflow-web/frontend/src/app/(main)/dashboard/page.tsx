'use client';

import { motion } from 'framer-motion';
import {
  Users,
  Briefcase,
  CheckCircle,
  DollarSign
} from 'lucide-react';
// T159: Code splitting - Dashboard components loaded dynamically
import dynamic from 'next/dynamic';
import { StatCardSkeleton, ChartSkeleton, ListSkeleton } from '@/components/ui/Skeleton';
import { useDashboardStats, useTasksByStatus, useProjects, useTasks } from '@/lib/query';
import { ProjectDrawer } from '@/components/project/ProjectDrawer';
import { useProjectDrawer } from '@/hooks/useProjectDrawer';

// Dynamic imports for heavy dashboard components
const TaskDistributionChart = dynamic(
  () => import('@/components/dashboard/TaskDistributionChart').then(m => ({ default: m.TaskDistributionChart })),
  { loading: () => <ChartSkeleton />, ssr: true }
);
const UpcomingDeadlines = dynamic(
  () => import('@/components/dashboard/UpcomingDeadlines').then(m => ({ default: m.UpcomingDeadlines })),
  { loading: () => <ListSkeleton count={5} />, ssr: true }
);
const ProjectList = dynamic(
  () => import('@/components/dashboard/ProjectList').then(m => ({ default: m.ProjectList })),
  { loading: () => <ListSkeleton count={4} />, ssr: true }
);

// Regular import for StatCard (lightweight, used frequently)
import { StatCard } from '@/components/dashboard/StatCard';

export default function DashboardPage() {
  // Use React Query hooks for data fetching
  const { data: statsData, isLoading: statsLoading } = useDashboardStats();
  const { data: chartData, isLoading: chartLoading } = useTasksByStatus();
  const { data: projectsData, isLoading: projectsLoading } = useProjects();
  const { data: tasksData } = useTasks();

  // Project drawer for editing
  const {
    isDrawerOpen,
    selectedProject,
    openDrawer,
    closeDrawer,
  } = useProjectDrawer();

  // Calculate total tasks for chart
  const totalTasks = chartData?.reduce((sum, item) => sum + item.value, 0) || 0;

  // Filter out archived tasks for calculations
  const activeTasks = tasksData?.filter(t => t.status !== 'ARCHIVED') || [];

  // Prepare projects data with correct progress calculation
  const projectsList = projectsData && projectsData.length > 0
    ? projectsData.map((project: any) => {
        // Calculate actual progress based on tasks
        const projectTasks = activeTasks.filter(t => t.project_id === project.id);
        const completedTasks = projectTasks.filter(t => t.status === 'DONE').length;
        const progress = projectTasks.length > 0
          ? Math.round((completedTasks / projectTasks.length) * 100)
          : 0;

        return {
          id: project.id,
          name: project.name,
          description: project.description,
          client: 'Teamflow Agency', // Default client name
          status: project.status as 'active' | 'on_hold' | 'completed',
          dueDate: project.created_at ? new Date(project.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'TBD',
          progress,
          created_at: project.created_at,
        };
      })
    : [];

  return (
    <>
      <div className="space-y-8 pb-8">
        {/* Header */}
        <div className="flex flex-col gap-1">
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold tracking-tight"
          >
            Dashboard
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-muted-foreground"
          >
            Agency overview and performance metrics.
          </motion.p>
        </div>

        {/* T153: Stats Grid with skeleton loading */}
        {statsLoading ? (
          <StatCardSkeleton />
        ) : statsData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Active Projects"
              value={statsData.activeProjects.toString()}
              icon={Briefcase}
              trend={{ value: statsData.trends?.activeProjects || 0, isPositive: true }}
              color="bg-primary"
              delay={0}
            />
            <StatCard
              title="Tasks Completed"
              value={statsData.tasksCompleted.toString()}
              icon={CheckCircle}
              trend={{ value: statsData.trends?.tasksCompleted || 0, isPositive: true }}
              color="bg-emerald-500"
              delay={1}
            />
            <StatCard
              title="Team Utilization"
              value={`${statsData.teamUtilization}%`}
              icon={Users}
              trend={{ value: statsData.trends?.teamUtilization || 0, isPositive: false }}
              color="bg-blue-500"
              delay={2}
            />
            <StatCard
              title="Revenue (YTD)"
              value={`$${(statsData.revenue / 1000).toFixed(1)}k`}
              icon={DollarSign}
              trend={{ value: statsData.trends?.revenue || 0, isPositive: true }}
              color="bg-purple-500"
              delay={3}
            />
          </div>
        ) : null}

        {/* Visualizations Grid with skeleton loading */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* T153: Chart skeleton */}
            {chartLoading ? (
              <ChartSkeleton />
            ) : (
              <TaskDistributionChart
                data={chartData || []}
                totalTasks={totalTasks}
              />
            )}
            {/* T153: Projects skeleton */}
            {projectsLoading ? (
              <ListSkeleton count={4} />
            ) : (
              <ProjectList projects={projectsList} onEdit={openDrawer} />
            )}
          </div>
          <div className="lg:col-span-1">
            <UpcomingDeadlines
              tasks={tasksData}
              projects={projectsData}
            />
          </div>
        </div>
      </div>

      {/* Project Drawer - Outside main container */}
      <ProjectDrawer
        isOpen={isDrawerOpen}
        onClose={closeDrawer}
        project={selectedProject}
      />
    </>
  );
}