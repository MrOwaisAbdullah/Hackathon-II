"use client";

import { motion } from "framer-motion";

export default function TeamPage() {
  const team = [
    { id: 1, name: "Alex Johnson", role: "Project Manager", avatar: "AJ", tasks: 8 },
    { id: 2, name: "Sarah Chen", role: "Designer", avatar: "SC", tasks: 12 },
    { id: 3, name: "Mike Brown", role: "Developer", avatar: "MB", tasks: 15 },
    { id: 4, name: "Emma Davis", role: "Developer", avatar: "ED", tasks: 10 },
    { id: 5, name: "Chris Wilson", role: "Designer", avatar: "CW", tasks: 6 },
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
            <h1 className="text-3xl font-bold mb-2">Team</h1>
            <p className="text-muted-foreground">Manage your team members</p>
          </div>
          <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 transition-opacity">
            Add Team Member
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {team.map((member, i) => (
            <motion.div
              key={member.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-lg border border-border p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                  {member.avatar}
                </div>
                <div>
                  <h3 className="font-semibold">{member.name}</h3>
                  <p className="text-sm text-muted-foreground">{member.role}</p>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Active Tasks</span>
                <span className="font-medium">{member.tasks}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
