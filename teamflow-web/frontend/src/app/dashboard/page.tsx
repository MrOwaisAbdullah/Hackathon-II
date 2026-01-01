
'use client';

import { motion } from 'framer-motion';
import { 
  Users, 
  Briefcase, 
  CheckCircle, 
  DollarSign 
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { TaskDistributionChart } from '@/components/dashboard/TaskDistributionChart';
import { WorkflowProgress } from '@/components/dashboard/WorkflowProgress';
import { ProjectList } from '@/components/dashboard/ProjectList';
import { useDashboardStats, useTasksByStatus } from '@/lib/query';

export default function DashboardPage() {
  // Use React Query hooks (data will be used when backend is ready)
  const { data: _statsData, isLoading: _statsLoading } = useDashboardStats();
  const { data: chartData, isLoading: _chartLoading } = useTasksByStatus();

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

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {fallbackStats.map((stat, i) => (
          <StatCard
            key={stat.title}
            {...stat}
            delay={i}
          />
        ))}
      </div>

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <TaskDistributionChart 
            data={chartData || fallbackChartData} 
            totalTasks={95}
          />
          <ProjectList projects={mockProjects} />
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