"use client";

import { motion } from "framer-motion";

export default function ProjectsPage() {
  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2">Projects</h1>
        <p className="text-muted-foreground mb-8">Manage your agency projects</p>

        <div className="grid gap-6">
          {/* Sample project cards */}
          {[
            { name: "Website Redesign", client: "Acme Corp", status: "In Progress", tasks: 12 },
            { name: "Mobile App", client: "StartUp Inc", status: "Planning", tasks: 8 },
            { name: "Brand Identity", client: "Local Cafe", status: "Completed", tasks: 24 },
          ].map((project, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-lg border border-border p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{project.name}</h3>
                  <p className="text-sm text-muted-foreground">{project.client}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  project.status === "Completed" ? "bg-green-100 text-green-800" :
                  project.status === "In Progress" ? "bg-blue-100 text-blue-800" :
                  "bg-gray-100 text-gray-800"
                }`}>
                  {project.status}
                </span>
              </div>
              <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
                <span>{project.tasks} tasks</span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
