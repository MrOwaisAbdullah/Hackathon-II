"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User as UserIcon, ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { AssigneeAvatar } from "./AssigneeAvatar";

interface User {
  id: string;
  name: string;
  email: string;
}

interface AssigneeSelectProps {
  users: User[];
  value?: string | null;
  onChange: (assigneeId: string | null) => void;
  currentAssignee?: User | null;
  label?: string;
  placeholder?: string;
  className?: string;
}

export function AssigneeSelect({
  users,
  value,
  onChange,
  currentAssignee,
  label = "Assign To",
  placeholder = "Unassigned",
  className,
}: AssigneeSelectProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Get the display user (either from current assignee or find in users list)
  const displayUser = currentAssignee || users.find((u) => u.id === value);

  const handleSelect = (userId: string | null) => {
    onChange(userId);
    setIsOpen(false);
  };

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <UserIcon className="w-4 h-4 text-accent" />
          {label}
        </label>
      )}

      <div className="relative">
        {/* Trigger Button */}
        <motion.button
          type="button"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            "w-full flex items-center justify-between gap-3 px-4 py-3",
            "bg-background border-2 rounded-xl text-left",
            "focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent",
            "transition-all duration-200",
            isOpen ? "border-accent ring-4 ring-accent/10" : "border-input hover:border-input/80"
          )}
        >
          <div className="flex items-center gap-3">
            {displayUser ? (
              <>
                <AssigneeAvatar name={displayUser.name} email={displayUser.email} size="md" />
                <span className="text-sm font-medium">{displayUser.name}</span>
              </>
            ) : (
              <>
                <div className="w-7 h-7 rounded-full border-2 border-dashed border-muted-foreground/30" />
                <span className="text-sm text-muted-foreground">{placeholder}</span>
              </>
            )}
          </div>
          <ChevronDown
            className={cn(
              "w-4 h-4 text-muted-foreground transition-transform",
              isOpen && "rotate-180"
            )}
          />
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
                className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-xl shadow-lg z-20 overflow-hidden max-h-64 overflow-y-auto scrollbar-lime"
              >
                <div className="p-1">
                  {/* Unassigned */}
                  <button
                    type="button"
                    onClick={() => handleSelect(null)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 rounded-lg",
                      "hover:bg-muted/50 transition-colors text-left",
                      !value && "bg-accent/10"
                    )}
                  >
                    <div className="w-7 h-7 rounded-full border-2 border-dashed border-muted-foreground/30" />
                    <span className="text-sm">{placeholder}</span>
                    {!value && (
                      <Check className="w-4 h-4 ml-auto text-accent" />
                    )}
                  </button>

                  {/* Team Members */}
                  {users.map((user) => (
                    <button
                      key={user.id}
                      type="button"
                      onClick={() => handleSelect(user.id)}
                      className={cn(
                        "w-full flex items-center gap-3 px-3 py-2 rounded-lg",
                        "hover:bg-muted/50 transition-colors text-left",
                        value === user.id && "bg-accent/10"
                      )}
                    >
                      <AssigneeAvatar name={user.name} email={user.email} size="md" />
                      <span className="text-sm font-medium">{user.name}</span>
                      {value === user.id && (
                        <Check className="w-4 h-4 ml-auto text-accent" />
                      )}
                    </button>
                  ))}
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
