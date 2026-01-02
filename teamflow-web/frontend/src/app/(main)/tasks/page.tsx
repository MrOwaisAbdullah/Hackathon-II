"use client";

// T159: Code splitting - TaskBoard is loaded dynamically
import dynamic from "next/dynamic";

const TaskBoard = dynamic(
  () => import("@/components/board/TaskBoard").then(mod => ({ default: mod.TaskBoard })),
  {
    loading: () => (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-muted/30 rounded-lg p-4 animate-pulse">
            <div className="h-6 bg-muted rounded mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((j) => (
                <div key={j} className="h-24 bg-muted rounded"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    ),
    ssr: false, // TaskBoard uses dnd-kit which requires client-side rendering
  }
);

export default function TasksPage() {
  return <TaskBoard />;
}
