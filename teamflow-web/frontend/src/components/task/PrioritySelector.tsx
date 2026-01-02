"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Flag, Check } from "lucide-react";
import type { TaskPriority } from "@/types/task";

interface PrioritySelectorProps {
  value: TaskPriority | null | undefined;
  onChange: (priority: TaskPriority) => void;
  disabled?: boolean;
}

// Updated Priority Colors for "DoQuanta" Theme
// Selected state now uses the Brand Lime Green to distinguish from the Black primary button
const PRIORITY_CONFIG: Record<
  TaskPriority,
  { label: string; color: string; activeClass: string; iconColor: string }
> = {
  LOW: {
    label: "Low",
    color: "text-zinc-500",
    // Lime 300/400 for active state - distinct from black submit button
    activeClass: "border-lime-500 bg-lime-400 text-black font-bold",
    iconColor: "text-black",
  },
  MEDIUM: {
    label: "Medium",
    color: "text-zinc-500",
    activeClass: "border-lime-500 bg-lime-400 text-black font-bold",
    iconColor: "text-black",
  },
  HIGH: {
    label: "High",
    color: "text-zinc-500",
    activeClass: "border-lime-500 bg-lime-400 text-black font-bold",
    iconColor: "text-black",
  },
};

export function PrioritySelector({
  value,
  onChange,
  disabled = false,
}: PrioritySelectorProps) {
  return (
    <div className="flex gap-2 w-full" data-testid="priority-selector">
      {(Object.keys(PRIORITY_CONFIG) as TaskPriority[]).map((priority) => {
        const config = PRIORITY_CONFIG[priority];
        const isSelected = value === priority;

        return (
          <motion.button
            key={priority}
            type="button"
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            onClick={() => !disabled && onChange(priority)}
            disabled={disabled}
            className={`
              flex-1 flex items-center justify-center gap-2 px-3 py-2.5
              border rounded-lg text-sm transition-all duration-200
              ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              ${
                isSelected
                  ? `${config.activeClass} shadow-sm ring-1 ring-lime-500`
                  : "bg-white border-zinc-300 text-zinc-700 hover:border-zinc-400 hover:bg-zinc-50 dark:bg-zinc-900 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 font-medium"
              }
            `}
          >
            <Flag 
              className={`w-4 h-4 ${isSelected ? "fill-black text-black" : "text-zinc-400 dark:text-zinc-500"}`} 
            />
            <span>{config.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
