
'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

interface DataPoint {
  label: string;
  value: number;
  color: string; // Tailwind bg class
}

interface TaskDistributionChartProps {
  data: DataPoint[];
  title?: string;
  totalTasks?: number;
}

export function TaskDistributionChart({ 
  data, 
  title = "Task Distribution",
  totalTasks = 0
}: TaskDistributionChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
      className="card-float p-5 rounded-lg h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-base text-foreground tracking-tight">{title}</h3>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground">
          Total: {totalTasks}
        </span>
      </div>

      <div className="space-y-4">
        {data.map((item, index) => (
          <div key={item.label} className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-muted-foreground">{item.label}</span>
              <span className="text-foreground tabular-nums">{item.value}</span>
            </div>
            
            {/* Progress Bar Background */}
            <div className="h-2 w-full bg-secondary/50 rounded-full overflow-hidden">
              {/* Animated Progress Fill */}
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(item.value / (totalTasks || 1)) * 100}%` }}
                transition={{ duration: 0.8, delay: 0.2 + (index * 0.05), ease: "easeOut" }}
                className={`h-full rounded-full ${item.color}`}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
