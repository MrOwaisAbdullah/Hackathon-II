
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
import { useDashboardStats, useTasksByStatus, useProjects } from '@/lib/query';

// Dynamic imports for heavy dashboard components
const TaskDistributionChart = dynamic(
  () => import('@/components/dashboard/TaskDistributionChart').then(m => ({ default: m.TaskDistributionChart })),
  { loading: () => <ChartSkeleton />, ssr: true }
);
const WorkflowProgress = dynamic(
  () => import('@/components/dashboard/WorkflowProgress').then(m => ({ default: m.WorkflowProgress })),
  { loading: () => <div className="bg-card rounded-lg p-6 border border-border shadow-sm h-64 animate-pulse" />, ssr: true }
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

  // Mock data for fallbacks/initial implementation
  const fallbackStats = [
    {
      title: "Active Projects",
      value: "12",
      icon: Briefcase,
      trend: { value: 8, isPositive: true },
      color: "bg-primary",
      delay: 0
    },
    {
      title: "Tasks Completed",
      value: "148",
      icon: CheckCircle,
      trend: { value: 12, isPositive: true },
      color: "bg-emerald-500",
      delay: 1
    },
    {
      title: "Team Utilization",
      value: "87%",
      icon: Users,
      trend: { value: 2, isPositive: false },
      color: "bg-blue-500", // Fallback color
      delay: 2
    },
    {
      title: "Revenue (YTD)",
      value: "$42.5k",
      icon: DollarSign,
      trend: { value: 15, isPositive: true },
      color: "bg-purple-500",
      delay: 3
    }
  ];

  const fallbackChartData = [
    { label: "Todo", value: 24, color: "bg-slate-400" },
    { label: "In Progress", value: 18, color: "bg-blue-500" },
    { label: "Review", value: 8, color: "bg-yellow-400" },
    { label: "Done", value: 45, color: "bg-emerald-500" }
  ];

  const mockProjects = [
    { id: '1', name: 'Website Redesign', client: 'Acme Corp', status: 'active' as const, dueDate: 'Mar 15', progress: 75 },
    { id: '2', name: 'Mobile App', client: 'TechStart', status: 'active' as const, dueDate: 'Apr 02', progress: 45 },
    { id: '3', name: 'Brand Identity', client: 'Studio One', status: 'on-hold' as const, dueDate: 'Feb 20', progress: 90 },
    { id: '4', name: 'Marketing Campaign', client: 'Global Systems', status: 'active' as const, dueDate: 'Mar 30', progress: 20 },
  ];

  const workflowSteps = [
    { id: '1', label: 'Project Kickoff', status: 'completed' as const, date: 'Jan 15' },
    { id: '2', label: 'Design Phase', status: 'completed' as const, date: 'Jan 28' },
    { id: '3', label: 'Development', status: 'current' as const, date: 'In Progress' },
    { id: '4', label: 'QA Testing', status: 'pending' as const },
    { id: '5', label: 'Deployment', status: 'pending' as const }
  ];

  return (
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
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {fallbackStats.map((stat, i) => (
            <StatCard
              key={stat.title}
              {...stat}
              delay={i}
            />
          ))}
        </div>
      )}

      {/* Visualizations Grid with skeleton loading */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* T153: Chart skeleton */}
          {chartLoading ? (
            <ChartSkeleton />
          ) : (
            <TaskDistributionChart
              data={chartData || fallbackChartData}
              totalTasks={95}
            />
          )}
          {/* T153: Projects skeleton */}
          {projectsLoading ? (
            <ListSkeleton count={4} />
          ) : (
            <ProjectList projects={projectsData && projectsData.length > 0 ? projectsData.map((p: any) => ({
              id: p.id,
              name: p.name,
              client: p.description || 'N/A',
              status: 'active' as const,
              dueDate: 'TBD',
              progress: 0
            })) : mockProjects} />
          )}
        </div>
        <div className="lg:col-span-1">
          <WorkflowProgress
            steps={workflowSteps}
          />
        </div>
      </div>
    </div>
  );
}