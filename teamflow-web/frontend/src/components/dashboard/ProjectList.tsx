
'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { MoreHorizontal, Calendar, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface Project {
  id: string;
  name: string;
  client: string;
  status: 'active' | 'completed' | 'on-hold';
  dueDate: string;
  progress: number;
}

interface ProjectListProps {
  projects: Project[];
}

export function ProjectList({ projects }: ProjectListProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-base text-foreground tracking-tight uppercase">Active Projects</h3>
        <Link 
          href="/projects" 
          className="text-xs font-bold text-lime-600 dark:text-lime-400 hover:underline flex items-center gap-0.5 transition-colors"
        >
          View All <ArrowRight size={12} />
        </Link>
      </div>

      <div className="grid gap-3">
        {projects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group flex items-center justify-between p-4 rounded-lg border border-border bg-card shadow-sm hover:shadow-md hover:border-lime-500/50 transition-all cursor-pointer"
          >
            <div className="flex items-center gap-4">
              {/* Status Indicator */}
              <div className={`w-3 h-3 rounded-sm ${
                project.status === 'active' ? 'bg-lime-500' : 
                project.status === 'on-hold' ? 'bg-amber-500' : 'bg-zinc-400'
              }`} />
              
              <div>
                <h4 className="font-bold text-sm text-foreground leading-none mb-1 group-hover:text-lime-600 dark:group-hover:text-lime-400 transition-colors">{project.name}</h4>
                <p className="text-[11px] text-muted-foreground font-medium uppercase tracking-wide">{project.client}</p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="hidden sm:flex flex-col items-end gap-1 min-w-[120px]">
                <div className="flex items-center gap-3 w-full">
                  <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${project.progress}%` }}
                      transition={{ duration: 1, delay: 0.5 + (index * 0.05) }}
                      className="h-full bg-lime-500 rounded-full"
                    />
                  </div>
                  <span className="text-[10px] font-bold w-8 text-right text-foreground tabular-nums">{project.progress}%</span>
                </div>
              </div>

              <div className="hidden sm:flex items-center gap-1.5 text-[10px] font-semibold text-muted-foreground bg-secondary px-2.5 py-1.5 rounded-md">
                <Calendar size={14} />
                <span className="tabular-nums">{project.dueDate}</span>
              </div>

              <button className="p-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-muted-foreground hover:text-foreground transition-colors opacity-0 group-hover:opacity-100">
                <MoreHorizontal size={18} />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
