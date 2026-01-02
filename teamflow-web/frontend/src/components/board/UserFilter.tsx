"use client";

import { useState } from "react";
import { useUsers } from "@/lib/query";
import { Filter, Check, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export type UserFilterValue = "all" | "unassigned" | string; // "all" | "unassigned" | userId

interface UserFilterProps {
  value: UserFilterValue;
  onChange: (value: UserFilterValue) => void;
  currentUserId?: string;
}

export function UserFilter({ value, onChange, currentUserId }: UserFilterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: users = [], isLoading: isLoadingUsers } = useUsers();

  const getFilterLabel = () => {
    if (value === "all") return "All Tasks";
    if (value === "unassigned") return "Unassigned";
    if (value === "my-tasks") return "My Tasks";
    const user = users.find((u) => u.id === value);
    return user?.name || "All Tasks";
  };

  return (
    <div className="relative" data-testid="user-filter">
      {/* Trigger Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-card border border-border rounded-lg hover:bg-muted/50 transition-colors"
      >
        <Filter className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm font-medium">{getFilterLabel()}</span>
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />

            {/* Dropdown Menu */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 mt-2 w-64 bg-card border border-border rounded-lg shadow-lg z-20 overflow-hidden"
            >
              <div className="p-1">
                {/* All Tasks */}
                <button
                  onClick={() => {
                    onChange("all");
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <Filter className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <span className="text-sm font-medium">All Tasks</span>
                  {value === "all" && (
                    <Check className="w-4 h-4 text-primary ml-auto" />
                  )}
                </button>

                {/* My Tasks */}
                {currentUserId && (
                  <button
                    onClick={() => {
                      onChange("my-tasks");
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                  >
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-sm font-medium">My Tasks</span>
                    {value === "my-tasks" && (
                      <Check className="w-4 h-4 text-primary ml-auto" />
                    )}
                  </button>
                )}

                {/* Unassigned */}
                <button
                  onClick={() => {
                    onChange("unassigned");
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <span className="text-xs text-muted-foreground">—</span>
                  </div>
                  <span className="text-sm font-medium">Unassigned</span>
                  {value === "unassigned" && (
                    <Check className="w-4 h-4 text-primary ml-auto" />
                  )}
                </button>

                {/* Divider */}
                {users.length > 0 && (
                  <div className="my-2 border-t border-border" />
                )}

                {/* Team Members */}
                {isLoadingUsers ? (
                  <div className="px-3 py-2 text-sm text-muted-foreground">
                    Loading team members...
                  </div>
                ) : (
                  users.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => {
                        onChange(user.id);
                        setIsOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                    >
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-primary/30 flex items-center justify-center">
                        <span className="text-xs font-semibold text-primary">
                          {user.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm font-medium">{user.name}</span>
                      {value === user.id && (
                        <Check className="w-4 h-4 text-primary ml-auto" />
                      )}
                    </button>
                  ))
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
