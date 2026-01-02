"use client";

import { motion } from "framer-motion";

export default function TimeEntriesPage() {
  const entries = [
    { id: 1, task: "Design homepage mockup", project: "Website Redesign", duration: "2h 30m", date: "2026-01-01" },
    { id: 2, task: "API authentication", project: "Mobile App", duration: "4h 15m", date: "2026-01-01" },
    { id: 3, task: "Component library", project: "Website Redesign", duration: "3h 45m", date: "2025-12-31" },
    { id: 4, task: "Code review", project: "Mobile App", duration: "1h 20m", date: "2025-12-31" },
    { id: 5, task: "Meeting with client", project: "Brand Identity", duration: "1h 00m", date: "2025-12-30" },
  ];

  const totalHours = entries.reduce((sum, e) => {
    const [h, m] = e.duration.split(" ").map((s) => parseInt(s));
    return sum + h + m / 60;
  }, 0);

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Time Entries</h1>
            <p className="text-muted-foreground">Track time across projects</p>
          </div>
          <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 transition-opacity">
            Log Time
          </button>
        </div>

        <div className="mb-6 bg-card rounded-lg border border-border p-6">
          <h3 className="font-semibold mb-2">Total Hours This Week</h3>
          <p className="text-4xl font-bold text-primary">{totalHours.toFixed(1)}h</p>
        </div>

        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Task</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Project</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Duration</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => (
                <motion.tr
                  key={entry.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className="border-t border-border hover:bg-muted/30"
                >
                  <td className="px-6 py-4">{entry.task}</td>
                  <td className="px-6 py-4 text-muted-foreground">{entry.project}</td>
                  <td className="px-6 py-4 font-medium">{entry.duration}</td>
                  <td className="px-6 py-4 text-muted-foreground">{entry.date}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
