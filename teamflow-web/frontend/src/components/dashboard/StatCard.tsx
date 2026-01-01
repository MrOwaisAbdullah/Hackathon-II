'use client';

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
  color?: string; // Tailwind color class for icon background (e.g., 'bg-orange-500')
  delay?: number;
}

export function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  description,
  color = "bg-primary",
  delay = 0
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.1, ease: "easeOut" }}
      whileHover={{ y: -4, boxShadow: "0 12px 24px -10px rgba(0,0,0,0.15)" }}
      className="bg-card border border-border p-6 rounded-xl shadow-sm relative overflow-hidden group glass"
    >
      <div className="flex items-start justify-between z-10 relative">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-3xl font-bold tracking-tight text-foreground">{value}</h3>
          
          {(trend || description) && (
            <div className="flex items-center gap-2 mt-2">
              {trend && (
                <div className={`flex items-center text-xs font-medium px-1.5 py-0.5 rounded-full ${
                  trend.isPositive 
                    ? 'text-emerald-600 bg-emerald-500/10 dark:text-emerald-400' 
                    : 'text-rose-600 bg-rose-500/10 dark:text-rose-400'
                }`}>
                  {trend.isPositive ? <ArrowUpRight size={12} className="mr-1" /> : <ArrowDownRight size={12} className="mr-1" />}
                  {Math.abs(trend.value)}%
                </div>
              )}
              {description && (
                <span className="text-xs text-muted-foreground">{description}</span>
              )}
            </div>
          )}
        </div>
        
        <div className={`p-3 rounded-xl ${color} bg-opacity-10 text-opacity-100 ring-1 ring-inset ring-white/10`}>
          <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
      </div>
      
      {/* Decorative background element */}
      <div className={`absolute -right-6 -bottom-6 w-32 h-32 rounded-full ${color} opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 blur-2xl`} />
    </motion.div>
  );
}