'use client';

import { useEffect, useState, useCallback } from 'react';
import { api } from '@/lib/api';
import { DollarSign, TrendingUp, TrendingDown, Clock, BarChart3 } from 'lucide-react';

interface ProfitabilityData {
  project_id: string;
  project_name: string;
  total_tasks: number;
  completed_tasks: number;
  completion_percentage: number;
  total_hours: number;
  total_cost: number;
  total_revenue: number;
  profit: number;
  profit_margin: number;
}

interface ProfitabilityCardProps {
  projectId?: string;
}

export function ProfitabilityCard({ projectId }: ProfitabilityCardProps) {
  const [data, setData] = useState<ProfitabilityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfitability = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const endpoint = projectId
        ? `/api/v1/analytics/profitability/project/${projectId}`
        : '/api/v1/analytics/profitability';

      const response = await api.get<ProfitabilityData[]>(endpoint);
      setData(Array.isArray(response.data) ? response.data : [response.data]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load profitability data');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchProfitability();
  }, [fetchProfitability]);

  if (loading) {
    return (
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-muted rounded w-1/3"></div>
          <div className="h-8 bg-muted rounded"></div>
          <div className="h-8 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card rounded-xl border border-destructive/50 p-6">
        <p className="text-destructive text-sm">{error}</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-card rounded-xl border border-border p-6">
        <p className="text-muted-foreground text-sm">No profitability data available</p>
        <p className="text-xs text-muted-foreground mt-2">
          Add hourly rates to projects and log time entries to see profitability metrics.
        </p>
      </div>
    );
  }

  // Calculate totals for all projects
  const totals = data.reduce(
    (acc, item) => ({
      total_revenue: acc.total_revenue + item.total_revenue,
      total_cost: acc.total_cost + item.total_cost,
      total_hours: acc.total_hours + item.total_hours,
      profit: acc.profit + item.profit,
    }),
    { total_revenue: 0, total_cost: 0, total_hours: 0, profit: 0 }
  );

  const totalProfitMargin = totals.total_revenue > 0
    ? (totals.profit / totals.total_revenue) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Revenue"
          value={`$${totals.total_revenue.toFixed(2)}`}
          icon={<DollarSign className="h-5 w-5" />}
          color="text-accent"
          bgColor="bg-accent/10"
        />
        <SummaryCard
          title="Total Cost"
          value={`$${totals.total_cost.toFixed(2)}`}
          icon={<BarChart3 className="h-5 w-5" />}
          color="text-destructive"
          bgColor="bg-destructive/10"
        />
        <SummaryCard
          title="Total Profit"
          value={`$${totals.profit.toFixed(2)}`}
          icon={totals.profit >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
          color={totals.profit >= 0 ? "text-accent" : "text-destructive"}
          bgColor={totals.profit >= 0 ? "bg-accent/10" : "bg-destructive/10"}
        />
        <SummaryCard
          title="Total Hours"
          value={`${totals.total_hours.toFixed(1)}h`}
          icon={<Clock className="h-5 w-5" />}
          color="text-blue-500"
          bgColor="bg-blue-500/10"
        />
      </div>

      {/* Overall Profit Margin */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Overall Profit Margin</h3>
          <span className={`text-2xl font-bold ${totalProfitMargin >= 0 ? 'text-accent' : 'text-destructive'}`}>
            {totalProfitMargin.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              totalProfitMargin >= 20 ? 'bg-accent' :
              totalProfitMargin >= 10 ? 'bg-yellow-500' :
              totalProfitMargin >= 0 ? 'bg-orange-500' :
              'bg-destructive'
            }`}
            style={{ width: `${Math.max(0, Math.min(100, totalProfitMargin))}%` }}
          />
        </div>
      </div>

      {/* Project Breakdown */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="p-6 border-b border-border">
          <h3 className="text-lg font-semibold">Project Breakdown</h3>
        </div>
        <div className="divide-y divide-border">
          {data.map((project) => (
            <ProjectRow key={project.project_id} project={project} />
          ))}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  icon,
  color,
  bgColor,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}) {
  return (
    <div className="bg-card rounded-xl border border-border p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${bgColor} ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function ProjectRow({ project }: { project: ProfitabilityData }) {
  const isProfitable = project.profit >= 0;

  return (
    <div className="p-4 hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-medium mb-1">{project.project_name}</h4>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>{project.completed_tasks}/{project.total_tasks} tasks</span>
            <span>•</span>
            <span>{project.total_hours.toFixed(1)}h</span>
            <span>•</span>
            <span>{project.completion_percentage}% complete</span>
          </div>
        </div>
        <div className="text-right">
          <p className={`text-lg font-semibold ${isProfitable ? 'text-accent' : 'text-destructive'}`}>
            {isProfitable ? '+' : ''}${project.profit.toFixed(2)}
          </p>
          <p className={`text-xs ${project.profit_margin >= 20 ? 'text-accent' : project.profit_margin >= 0 ? 'text-yellow-500' : 'text-destructive'}`}>
            {project.profit_margin.toFixed(1)}% margin
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Completion</span>
          <span>{project.completion_percentage}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              project.completion_percentage >= 75 ? 'bg-accent' :
              project.completion_percentage >= 50 ? 'bg-yellow-500' :
              'bg-muted-foreground'
            }`}
            style={{ width: `${project.completion_percentage}%` }}
          />
        </div>
      </div>

      {/* Revenue/Cost breakdown */}
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div className="bg-muted/30 rounded-lg p-3">
          <p className="text-xs text-muted-foreground mb-1">Revenue</p>
          <p className="text-sm font-semibold text-accent">${project.total_revenue.toFixed(2)}</p>
        </div>
        <div className="bg-muted/30 rounded-lg p-3">
          <p className="text-xs text-muted-foreground mb-1">Cost</p>
          <p className="text-sm font-semibold text-destructive">${project.total_cost.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
}

export default ProfitabilityCard;
