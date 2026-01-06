"use client";

/**
 * ProfitabilityReport - Component for displaying project profitability metrics (US5 T135).
 *
 * Features:
 * - Displays profitability data for all projects
 * - Shows revenue, cost, profit, and profit margin
 * - Visual indicators for profitable/unprofitable projects
 * - Completion percentage tracking
 * - Total hours tracked per project
 */

import { useMemo, useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useProjectProfitability } from "@/lib/query";
import { TrendingUp, TrendingDown, DollarSign, Clock, CheckCircle } from "lucide-react";

export function ProfitabilityReport() {
  const [isDark, setIsDark] = useState(false);

  // Detect dark mode
  useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  // Profit margin badge styles - theme aware
  const positiveProfitStyle = {
    light: { backgroundColor: '#dcfce7', color: '#14532d' },
    dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
  };

  const negativeProfitStyle = {
    light: { backgroundColor: '#fee2e2', color: '#991b1b' },
    dark: { backgroundColor: 'rgba(127, 29, 29, 0.3)', color: '#f87171' },
  };

  const getProfitStyle = (isPositive: boolean) => {
    const base = isPositive ? positiveProfitStyle : negativeProfitStyle;
    return isDark ? base.dark : base.light;
  };
  const { data: profitabilityData = [], isLoading } = useProjectProfitability();

  // Calculate aggregate stats
  const aggregateStats = useMemo(() => {
    if (!profitabilityData || profitabilityData.length === 0) {
      return {
        totalRevenue: 0,
        totalCost: 0,
        totalProfit: 0,
        avgMargin: 0,
        totalHours: 0,
      };
    }

    const totalRevenue = profitabilityData.reduce(
      (sum: number, p: any) => sum + p.total_revenue,
      0
    );
    const totalCost = profitabilityData.reduce(
      (sum: number, p: any) => sum + p.total_cost,
      0
    );
    const totalProfit = profitabilityData.reduce(
      (sum: number, p: any) => sum + p.profit,
      0
    );
    const totalHours = profitabilityData.reduce(
      (sum: number, p: any) => sum + p.total_hours,
      0
    );
    const avgMargin =
      totalRevenue > 0 ? (totalProfit / totalRevenue) * 100 : 0;

    return {
      totalRevenue,
      totalCost,
      totalProfit,
      avgMargin,
      totalHours,
    };
  }, [profitabilityData]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-muted rounded w-1/3" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Aggregate Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-muted/30 rounded-lg border border-border"
        >
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <DollarSign className="w-4 h-4" />
            <span className="text-xs font-medium">Total Revenue</span>
          </div>
          <div className="text-lg font-semibold">
            {formatCurrency(aggregateStats.totalRevenue)}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="p-4 bg-muted/30 rounded-lg border border-border"
        >
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <DollarSign className="w-4 h-4" />
            <span className="text-xs font-medium">Total Cost</span>
          </div>
          <div className="text-lg font-semibold">
            {formatCurrency(aggregateStats.totalCost)}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`p-4 rounded-lg border ${
            aggregateStats.totalProfit >= 0
              ? "bg-green-500/10 border-green-500/30"
              : "bg-red-500/10 border-red-500/30"
          }`}
        >
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            {aggregateStats.totalProfit >= 0 ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
            <span className="text-xs font-medium">Net Profit</span>
          </div>
          <div
            className={`text-lg font-semibold ${
              aggregateStats.totalProfit >= 0
                ? "text-green-500"
                : "text-red-500"
            }`}
          >
            {formatCurrency(aggregateStats.totalProfit)}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="p-4 bg-muted/30 rounded-lg border border-border"
        >
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <Clock className="w-4 h-4" />
            <span className="text-xs font-medium">Total Hours</span>
          </div>
          <div className="text-lg font-semibold">
            {aggregateStats.totalHours.toFixed(1)}h
          </div>
        </motion.div>
      </div>

      {/* Project List */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-muted-foreground">
          Project Breakdown
        </h3>

        {profitabilityData.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>No profitability data available yet.</p>
            <p className="text-sm mt-2">
              Start tracking time to see profitability metrics.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {profitabilityData.map((project: any, index: number) => (
              <motion.div
                key={project.project_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 bg-card rounded-lg border border-border hover:bg-muted/30 transition-colors"
              >
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold">{project.project_name}</h4>
                      <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          {project.completed_tasks}/{project.total_tasks} tasks
                        </span>
                        <span>{project.completion_percentage}% complete</span>
                      </div>
                    </div>
                    <div
                      className="px-2 py-1 rounded text-xs font-medium"
                      style={getProfitStyle(project.profit >= 0)}
                    >
                      {formatPercent(project.profit_margin)}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${project.completion_percentage}%` }}
                      transition={{ duration: 0.5 }}
                      className="h-full bg-primary rounded-full"
                    />
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-4 gap-2 text-sm">
                    <div>
                      <div className="text-muted-foreground text-xs">Hours</div>
                      <div className="font-medium">{project.total_hours.toFixed(1)}h</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground text-xs">Revenue</div>
                      <div className="font-medium">
                        {formatCurrency(project.total_revenue)}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground text-xs">Cost</div>
                      <div className="font-medium">
                        {formatCurrency(project.total_cost)}
                      </div>
                    </div>
                    <div>
                      <div
                        className={`text-xs ${
                          project.profit >= 0 ? "text-green-500" : "text-red-500"
                        }`}
                      >
                        Profit
                      </div>
                      <div
                        className={`font-medium ${
                          project.profit >= 0 ? "text-green-500" : "text-red-500"
                        }`}
                      >
                        {formatCurrency(project.profit)}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
