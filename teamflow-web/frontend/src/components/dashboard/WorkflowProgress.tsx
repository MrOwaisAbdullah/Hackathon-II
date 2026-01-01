'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Clock, AlertCircle } from 'lucide-react';

interface Step {
  id: string;
  label: string;
  status: 'completed' | 'current' | 'pending' | 'error';
  date?: string;
}

interface WorkflowProgressProps {
  title?: string;
  steps: Step[];
}

export function WorkflowProgress({ 
  title = "Project Workflow", 
  steps 
}: WorkflowProgressProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="bg-card border border-border p-6 rounded-xl shadow-sm glass h-full"
    >
      <div className="mb-6">
        <h3 className="font-semibold text-lg">{title}</h3>
      </div>

      <div className="relative">
        {/* Vertical line connecting steps */}
        <div className="absolute left-3.5 top-2 bottom-4 w-0.5 bg-border/50 -z-10" />

        <div className="space-y-6">
          {steps.map((step, index) => (
            <motion.div 
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.5 + (index * 0.1) }}
              className="flex items-start gap-4"
            >
              <div className="relative z-10 bg-card rounded-full">
                {step.status === 'completed' && (
                  <CheckCircle2 className="w-7 h-7 text-emerald-500 fill-emerald-500/10" />
                )}
                {step.status === 'current' && (
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping" />
                    <Clock className="w-7 h-7 text-primary fill-primary/10 relative z-10" />
                  </div>
                )}
                {step.status === 'pending' && (
                  <Circle className="w-7 h-7 text-muted-foreground/40" />
                )}
                {step.status === 'error' && (
                  <AlertCircle className="w-7 h-7 text-destructive fill-destructive/10" />
                )}
              </div>

              <div className="flex-1 pt-0.5">
                <div className="flex justify-between items-start">
                  <h4 className={`text-sm font-medium ${step.status === 'current' ? 'text-primary' : 'text-foreground'}`}>
                    {step.label}
                  </h4>
                  {step.date && (
                    <span className="text-xs text-muted-foreground">{step.date}</span>
                  )}
                </div>
                {step.status === 'current' && (
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: "60%" }}
                    className="h-1 bg-primary/20 rounded-full mt-2 overflow-hidden"
                  >
                    <motion.div 
                      className="h-full bg-primary"
                      animate={{ x: ["-100%", "100%"] }}
                      transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    />
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}