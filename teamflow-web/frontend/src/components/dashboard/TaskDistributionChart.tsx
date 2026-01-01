'use client';

import { motion } from 'framer-motion';

interface DataPoint {
  label: string;
  value: number;
  color: string;
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
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-card border border-border p-6 rounded-xl shadow-sm glass h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-lg">{title}</h3>
        <span className="text-xs font-medium px-2 py-1 rounded-full bg-secondary/10 text-muted-foreground">
          Total: {totalTasks}
        </span>
      </div>

      <div className="space-y-4">
        {data.map((item, index) => (
          <div key={item.label} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-muted-foreground">{item.label}</span>
              <span className="font-bold text-foreground">{item.value}</span>
            </div>
            
            <div className="h-2 w-full bg-secondary/20 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(item.value / (totalTasks || 1)) * 100}%` }}
                transition={{ duration: 1, delay: 0.4 + (index * 0.1), ease: "easeOut" }}
                className={`h-full rounded-full ${item.color}`}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}