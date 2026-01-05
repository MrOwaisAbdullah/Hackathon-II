
'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  description?: string;
  color?: string;
  bgColor?: string;
  delay?: number;
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  description,
  delay = 0
}: StatCardProps) {
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

  // Trend badge styles - theme aware
  const positiveStyle = {
    light: { backgroundColor: '#dcfce7', color: '#14532d' },
    dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
  };

  const negativeStyle = {
    light: { backgroundColor: '#fee2e2', color: '#991b1b' },
    dark: { backgroundColor: 'rgba(127, 29, 29, 0.3)', color: '#f87171' },
  };

  const getTrendStyle = (isPositive: boolean) => {
    const base = isPositive ? positiveStyle : negativeStyle;
    return isDark ? base.dark : base.light;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.05, ease: [0.16, 1, 0.3, 1] }}
      className="card-float hover-lift p-3 md:p-5 rounded-lg group relative overflow-hidden bg-card border border-border"
    >
      <div className="flex items-start justify-between z-10 relative">
        <div className="space-y-1.5">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{title}</p>
          <div className="flex items-baseline gap-2">
            <h3 className="text-3xl font-black tracking-tight text-foreground tabular-nums">{value}</h3>
          </div>

          {(trend || description) && (
            <div className="flex items-center gap-2 pt-1">
              {trend && (
                <div
                  className="flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full"
                  style={getTrendStyle(trend.isPositive)}
                >
                  {trend.isPositive ? <ArrowUpRight size={10} className="mr-0.5" /> : <ArrowDownRight size={10} className="mr-0.5" />}
                  {Math.abs(trend.value)}%
                </div>
              )}
              {description && (
                <span className="text-[10px] text-muted-foreground">{description}</span>
              )}
            </div>
          )}
        </div>

        {/* Icon Container - Refined for "DoQuanta" look
          Light mode: Black background with Lime icon (High contrast, modern)
          Dark mode: Lime background with Black icon (Glowing, premium)
        */}
        <div className="p-2.5 rounded-xl bg-zinc-950 dark:bg-lime-400 text-lime-400 dark:text-zinc-950 shadow-sm ring-1 ring-white/10">
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}
