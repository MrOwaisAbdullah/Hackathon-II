/** Animated task distribution bar chart. */
'use client';

import { motion } from 'framer-motion';

interface TaskData {
  status: string;
  count: number;
  color: string;
}

interface TaskDistributionChartProps {
  data: TaskData[];
  total?: number;
}

export function TaskDistributionChart({ data, total }: TaskDistributionChartProps) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);
  const calculatedTotal = total ?? data.reduce((sum, d) => sum + d.count, 0);

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">Task Distribution</h3>

      <div className="space-y-4">
        {data.map((item, index) => {
          const percentage = (item.count / calculatedTotal) * 100;
          const barWidth = (item.count / maxCount) * 100;

          return (
            <motion.div
              key={item.status}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.4 }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">{item.status}</span>
                <span className="text-sm text-muted-foreground">
                  {item.count} ({percentage.toFixed(0)}%)
                </span>
              </div>

              <div className="h-3 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${barWidth}%` }}
                  transition={{ delay: index * 0.1 + 0.2, duration: 0.6, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
