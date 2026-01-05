
'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

interface DataPoint {
  label: string;
  value: number;
  color: string; // Hex color code
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
  const [isDark, setIsDark] = React.useState(false);

  // Detect dark mode
  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  // Total badge style - theme aware
  const totalBadgeStyle = {
    light: { backgroundColor: '#f3f4f6', color: '#1f2937' },
    dark: { backgroundColor: 'rgba(55, 65, 81, 0.5)', color: '#d1d5db' },
  };

  const finalStyle = isDark ? totalBadgeStyle.dark : totalBadgeStyle.light;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
      className="card-float p-5 rounded-lg"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-base text-foreground tracking-tight">{title}</h3>
        <span
          className="text-xs font-semibold px-2.5 py-1 rounded-md"
          style={finalStyle}
        >
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
              {/* Animated Progress Fill with inline style */}
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(item.value / (totalTasks || 1)) * 100}%` }}
                transition={{ duration: 0.8, delay: 0.2 + (index * 0.05), ease: "easeOut" }}
                className="h-full rounded-full"
                style={{ backgroundColor: item.color }}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
