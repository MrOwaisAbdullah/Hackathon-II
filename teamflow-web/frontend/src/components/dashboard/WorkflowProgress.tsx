'use client';

import * as React from 'react';
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

  // Date badge style - theme aware
  const dateBadgeStyle = {
    light: { backgroundColor: '#f3f4f6', color: '#6b7280' },
    dark: { backgroundColor: 'rgba(55, 65, 81, 0.5)', color: '#9ca3af' },
  };

  const finalDateStyle = isDark ? dateBadgeStyle.dark : dateBadgeStyle.light;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.15, ease: "easeOut" }}
      className="card-float p-6 rounded-lg h-full"
    >
      <div className="mb-6 border-b border-border pb-4">
        <h3 className="font-bold text-base text-foreground tracking-tight uppercase">{title}</h3>
      </div>

      <div className="relative pl-1">
        {/* Vertical Connector Line */}
        <div className="absolute left-[1.15rem] top-3 bottom-4 w-px bg-border -z-10" />

        <div className="space-y-6">
          {steps.map((step, index) => (
            <motion.div 
              key={step.id}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.2 + (index * 0.05) }}
              className="flex items-start gap-4"
            >
              <div className="relative z-10 bg-card rounded-full ring-4 ring-card">
                {step.status === 'completed' && (
                  <CheckCircle2 className="w-6 h-6 text-lime-500 fill-lime-100 dark:fill-lime-900/20" />
                )}
                {step.status === 'current' && (
                  <div className="relative">
                    <div className="absolute inset-0 bg-lime-400/30 rounded-full animate-ping" />
                    <Clock className="w-6 h-6 text-lime-600 dark:text-lime-400 relative z-10" />
                  </div>
                )}
                {step.status === 'pending' && (
                  <Circle className="w-6 h-6 text-muted-foreground/30" />
                )}
                {step.status === 'error' && (
                  <AlertCircle className="w-6 h-6 text-destructive" />
                )}
              </div>

              <div className="flex-1 pt-0.5">
                <div className="flex justify-between items-start">
                  <h4 className={`text-sm font-bold leading-none ${step.status === 'current' ? 'text-lime-600 dark:text-lime-400' : 'text-foreground'}`}>
                    {step.label}
                  </h4>
                  {step.date && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm" style={finalDateStyle}>{step.date}</span>
                  )}
                </div>
                {step.status === 'current' && (
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: "40%" }}
                    className="h-1 bg-lime-100 dark:bg-lime-900/30 rounded-full mt-2 overflow-hidden"
                  >
                    <motion.div 
                      className="h-full bg-lime-500"
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