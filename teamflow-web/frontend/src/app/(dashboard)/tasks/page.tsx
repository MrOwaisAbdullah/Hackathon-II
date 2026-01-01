"use client";

import { motion } from "framer-motion";

export default function TasksPage() {
  const columns = [
    { id: "todo", title: "To Do", tasks: [
      { id: 1, title: "Design homepage mockup", priority: "high" },
      { id: 2, title: "Create component library", priority: "medium" },
    ]},
    { id: "doing", title: "In Progress", tasks: [
      { id: 3, title: "Implement authentication", priority: "high" },
    ]},
    { id: "review", title: "In Review", tasks: [
      { id: 4, title: "API endpoint testing", priority: "medium" },
    ]},
    { id: "done", title: "Done", tasks: [
      { id: 5, title: "Setup project structure", priority: "low" },
      { id: 6, title: "Configure Tailwind CSS", priority: "low" },
    ]},
  ];

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2">Task Board</h1>
        <p className="text-muted-foreground mb-8">Drag and drop tasks to update status</p>

        <div className="grid grid-cols-4 gap-4">
          {columns.map((column, colIndex) => (
            <motion.div
              key={column.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: colIndex * 0.1 }}
              className="bg-muted/30 rounded-lg p-4"
            >
              <h2 className="font-semibold mb-4 flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary/20"></span>
                {column.title}
                <span className="text-sm text-muted-foreground">({column.tasks.length})</span>
              </h2>
              <div className="space-y-3">
                {column.tasks.map((task) => (
                  <motion.div
                    key={task.id}
                    whileHover={{ scale: 1.02 }}
                    className="bg-card rounded-lg p-4 border border-border shadow-sm cursor-pointer"
                  >
                    <p className="font-medium text-sm">{task.title}</p>
                    <span className={`inline-block mt-2 px-2 py-0.5 rounded text-xs ${
                      task.priority === "high" ? "bg-red-100 text-red-700" :
                      task.priority === "medium" ? "bg-yellow-100 text-yellow-700" :
                      "bg-gray-100 text-gray-700"
                    }`}>
                      {task.priority}
                    </span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
