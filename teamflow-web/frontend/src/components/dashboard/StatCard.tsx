
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
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.05, ease: [0.16, 1, 0.3, 1] }}
      className="card-float hover-lift p-5 rounded-lg group relative overflow-hidden bg-card border border-border"
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
                <div className={`flex items-center text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                  trend.isPositive 
                    ? 'text-lime-700 bg-lime-100 dark:text-lime-400 dark:bg-lime-900/30' 
                    : 'text-rose-700 bg-rose-100 dark:text-rose-400 dark:bg-rose-900/30'
                }`}>
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
        
        {/* 
          Icon Container - Refined for "DoQuanta" look
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
