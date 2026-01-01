
'use client';

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
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-lg">Active Projects</h3>
        <Link 
          href="/projects" 
          className="text-sm text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
        >
          View All <ArrowRight size={14} />
        </Link>
      </div>

      <div className="grid gap-4">
        {projects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.01, backgroundColor: "rgba(var(--background), 0.5)" }}
            className="group flex items-center justify-between p-4 rounded-xl border border-border bg-card/50 hover:bg-card hover:shadow-sm transition-all cursor-pointer"
          >
            <div className="flex items-center gap-4">
              <div className={`w-2 h-2 rounded-full ${
                project.status === 'active' ? 'bg-emerald-500' : 
                project.status === 'on-hold' ? 'bg-amber-500' : 'bg-slate-400'
              }`} />
              
              <div>
                <h4 className="font-medium text-sm text-foreground">{project.name}</h4>
                <p className="text-xs text-muted-foreground">{project.client}</p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="hidden sm:flex flex-col items-end gap-1 min-w-[100px]">
                <div className="flex items-center gap-2 w-full">
                  <div className="h-1.5 w-full bg-secondary/20 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${project.progress}%` }}
                      transition={{ duration: 1, delay: 0.5 + (index * 0.1) }}
                      className="h-full bg-primary rounded-full"
                    />
                  </div>
                  <span className="text-xs font-medium w-8 text-right">{project.progress}%</span>
                </div>
              </div>

              <div className="hidden sm:flex items-center gap-1 text-xs text-muted-foreground bg-secondary/10 px-2 py-1 rounded-md">
                <Calendar size={12} />
                <span>{project.dueDate}</span>
              </div>

              <button className="p-1 rounded-md hover:bg-secondary/20 text-muted-foreground hover:text-foreground transition-colors opacity-0 group-hover:opacity-100">
                <MoreHorizontal size={16} />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
