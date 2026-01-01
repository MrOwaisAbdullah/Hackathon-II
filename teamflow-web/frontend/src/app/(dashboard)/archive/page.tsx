"use client";

import { motion } from "framer-motion";

export default function ArchivePage() {
  const archivedTasks = [
    { id: 1, title: "Old landing page design", project: "Website Redesign", archivedOn: "2025-12-15" },
    { id: 2, title: "Initial API prototype", project: "Mobile App", archivedOn: "2025-12-10" },
    { id: 3, title: "Draft brand guidelines", project: "Brand Identity", archivedOn: "2025-12-05" },
    { id: 4, title: "Unused component", project: "Website Redesign", archivedOn: "2025-11-28" },
  ];

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Archived Tasks</h1>
            <p className="text-muted-foreground">View and restore archived tasks</p>
          </div>
        </div>

        <div className="space-y-4">
          {archivedTasks.map((task, i) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-lg border border-border p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{task.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{task.project}</p>
                  <p className="text-xs text-muted-foreground mt-2">Archived on {task.archivedOn}</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 text-sm border border-border rounded hover:bg-muted transition-colors">
                    View
                  </button>
                  <button className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:opacity-90 transition-opacity">
                    Restore
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {archivedTasks.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 text-muted-foreground"
          >
            <p>No archived tasks</p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
