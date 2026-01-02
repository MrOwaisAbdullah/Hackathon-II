"use client";

import { useDroppable } from "@dnd-kit/core";
import { useUsers } from "@/lib/query";
import { motion } from "framer-motion";
import { Users } from "lucide-react";

interface TeamMemberListProps {
  onAssignTask?: (userId: string | null) => void;
  currentUserId?: string;
}

export function TeamMemberList({ onAssignTask, currentUserId }: TeamMemberListProps) {
  const { data: users = [], isLoading } = useUsers();
  const { setNodeRef } = useDroppable({
    id: "team-members",
    data: {
      type: "team-members",
      action: "assign",
    },
  });

  const handleMemberClick = (userId: string | null) => {
    if (onAssignTask) {
      onAssignTask(userId);
    }
  };

  return (
    <div className="bg-card rounded-lg border border-border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Users className="w-4 h-4 text-muted-foreground" />
          Team Members
        </h3>
        <span className="text-xs text-muted-foreground">{users.length} members</span>
      </div>

      <div
        ref={setNodeRef}
        className="flex flex-wrap gap-2"
        data-testid="team-member-list"
      >
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : (
          <>
            {/* Unassigned option */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleMemberClick(null)}
              className="w-10 h-10 rounded-full bg-muted border-2 border-dashed border-border flex items-center justify-center hover:border-primary/50 hover:bg-muted/50 transition-colors"
              data-testid="team-avatar-unassigned"
              title="Unassigned"
            >
              <span className="text-xs text-muted-foreground">—</span>
            </motion.button>

            {/* Team members */}
            {users.map((user, index) => (
              <motion.button
                key={user.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleMemberClick(user.id)}
                className={`w-10 h-10 rounded-full bg-gradient-to-br flex items-center justify-center transition-all ${
                  user.id === currentUserId
                    ? "from-primary to-primary/70 ring-2 ring-primary ring-offset-2"
                    : "from-primary/20 to-primary/30 hover:from-primary/30 hover:to-primary/40"
                }`}
                data-testid="team-avatar"
                data-user-id={user.id}
                title={user.name}
              >
                <span className="text-xs font-semibold text-primary">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </motion.button>
            ))}
          </>
        )}
      </div>

      {/* Drop zone hint */}
      <div className="mt-3 text-xs text-muted-foreground text-center">
        Drop a task on a member to assign
      </div>
    </div>
  );
}
