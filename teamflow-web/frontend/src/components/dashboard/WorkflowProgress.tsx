/** Animated workflow progress component with step indicators. */
'use client';

import { motion } from 'framer-motion';

interface Step {
  id: string;
  label: string;
  count: number;
  completed: boolean;
}

interface WorkflowProgressProps {
  steps: Step[];
}

export function WorkflowProgress({ steps }: WorkflowProgressProps) {
  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <h3 className="text-lg font-semibold text-foreground mb-6">Workflow Progress</h3>

      <div className="relative">
        {/* Connection line */}
        <div className="absolute top-4 left-0 right-0 h-1 bg-muted">
          <motion.div
            initial={{ width: 0 }}
            animate={{
              width: `${(steps.filter((s) => s.completed).length / Math.max(steps.length, 1)) * 100}%`,
            }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-full bg-primary rounded-full"
          />
        </div>

        {/* Steps */}
        <div className="flex justify-between relative">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.4 }}
              className="flex flex-col items-center gap-2 flex-1"
            >
              {/* Step indicator */}
              <motion.div
                animate={{
                  scale: step.completed ? [1, 1.1, 1] : 1,
                }}
                transition={{
                  duration: 0.3,
                  delay: index * 0.1 + 0.5,
                  scale: { repeat: step.completed ? 1 : 0, repeatDelay: 2 },
                }}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold z-10 ${
                  step.completed
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {step.completed ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  index + 1
                )}
              </motion.div>

              {/* Step label */}
              <div className="text-center">
                <p className="text-xs font-medium text-foreground">{step.label}</p>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.1 + 0.3 }}
                  className="text-xs text-muted-foreground"
                >
                  {step.count} tasks
                </motion.p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
