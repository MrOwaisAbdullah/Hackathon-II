import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <motion.div
      initial={{ opacity: 0.5 }}
      animate={{ opacity: 1 }}
      transition={{
        repeat: Infinity,
        duration: 1.5,
        ease: "easeInOut",
      }}
      className={`bg-muted rounded ${className}`}
    />
  );
}

interface TaskCardSkeletonProps {
  count?: number;
}

export function TaskCardSkeleton({ count = 3 }: TaskCardSkeletonProps) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-card rounded-lg p-4 border border-border shadow-sm"
        >
          <Skeleton className="h-4 w-20 mb-3" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-2/3 mb-4" />
          <div className="flex justify-between">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-5 w-5 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

interface StatCardSkeletonProps {
  count?: number;
}

export function StatCardSkeleton({ count = 4 }: StatCardSkeletonProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-card rounded-lg p-6 border border-border shadow-sm"
        >
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-8 w-16 mb-2" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  );
}

// T153: Chart skeleton for visualizations
interface ChartSkeletonProps {
  className?: string;
}

export function ChartSkeleton({ className = "" }: ChartSkeletonProps) {
  return (
    <div className={`bg-card rounded-lg p-6 border border-border shadow-sm ${className}`}>
      <Skeleton className="h-4 w-32 mb-4" />
      <div className="flex items-end justify-between gap-2 h-48">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-2">
            <Skeleton className="w-full h-full min-h-[100px]" style={{ height: `${60 + Math.random() * 80}px` }} />
          </div>
        ))}
      </div>
    </div>
  );
}

// T153: List skeleton for project/task lists
interface ListSkeletonProps {
  count?: number;
  className?: string;
}

export function ListSkeleton({ count = 4, className = "" }: ListSkeletonProps) {
  return (
    <div className={`bg-card rounded-lg p-6 border border-border shadow-sm ${className}`}>
      <Skeleton className="h-4 w-32 mb-4" />
      <div className="space-y-3">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
            <div className="space-y-2">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-24" />
            </div>
            <Skeleton className="h-6 w-16" />
          </div>
        ))}
      </div>
    </div>
  );
}

// T153: Workflow step skeleton
interface WorkflowSkeletonProps {
  steps?: number;
}

export function WorkflowSkeleton({ steps = 5 }: WorkflowSkeletonProps) {
  return (
    <div className="bg-card rounded-lg p-6 border border-border shadow-sm">
      <Skeleton className="h-4 w-32 mb-6" />
      <div className="space-y-4">
        {Array.from({ length: steps }).map((_, i) => (
          <div key={i} className="flex items-start gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
