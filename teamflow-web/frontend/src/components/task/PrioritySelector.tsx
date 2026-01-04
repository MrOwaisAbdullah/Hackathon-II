"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Flag, Check } from "lucide-react";
import { TaskPriority } from "@/types";
import { cn } from "@/lib/utils";

interface PrioritySelectorProps {
  value: TaskPriority | null | undefined;
  onChange: (priority: TaskPriority) => void;
  disabled?: boolean;
}

export function PrioritySelector({
  value,
  onChange,
  disabled = false,
}: PrioritySelectorProps) {
  const [hoveredPriority, setHoveredPriority] = useState<TaskPriority | null>(null);
  const [isDark, setIsDark] = useState(false);

  // Detect dark mode
  useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  // Priority styles
  const getPriorityStyles = (priority: TaskPriority) => {
    const styles = {
      LOW: {
        label: "Low",
        description: "Can wait",
        selected: { backgroundColor: '#22c55e', color: '#ffffff' },
        normal: { backgroundColor: '#dcfce7', color: '#14532d' },
        selectedDark: { backgroundColor: '#22c55e', color: '#ffffff' },
        normalDark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
        hover: { backgroundColor: '#bbf7d0' },
        hoverDark: { backgroundColor: 'rgba(20, 83, 45, 0.5)' },
      },
      MEDIUM: {
        label: "Medium",
        description: "Normal pace",
        selected: { backgroundColor: '#eab308', color: '#ffffff' },
        normal: { backgroundColor: '#fef9c3', color: '#713f12' },
        selectedDark: { backgroundColor: '#eab308', color: '#ffffff' },
        normalDark: { backgroundColor: 'rgba(113, 63, 18, 0.3)', color: '#facc15' },
        hover: { backgroundColor: '#fef08a' },
        hoverDark: { backgroundColor: 'rgba(113, 63, 18, 0.5)' },
      },
      HIGH: {
        label: "High",
        description: "Urgent",
        selected: { backgroundColor: '#ef4444', color: '#ffffff' },
        normal: { backgroundColor: '#fee2e2', color: '#7f1d1d' },
        selectedDark: { backgroundColor: '#ef4444', color: '#ffffff' },
        normalDark: { backgroundColor: 'rgba(127, 29, 29, 0.3)', color: '#f87171' },
        hover: { backgroundColor: '#fecaca' },
        hoverDark: { backgroundColor: 'rgba(127, 29, 29, 0.5)' },
      },
    };
    return styles[priority];
  };

  return (
    <div className="grid grid-cols-3 gap-2 w-full" data-testid="priority-selector">
      {(Object.values(TaskPriority) as TaskPriority[]).map((priority, index) => {
        const styles = getPriorityStyles(priority);
        const isSelected = value === priority;
        const isHovered = hoveredPriority === priority;

        const baseStyle = isSelected ? styles.selected : styles.normal;
        const baseStyleDark = isSelected ? styles.selectedDark : styles.normalDark;
        const hoverStyle = isHovered ? (isDark ? styles.hoverDark : styles.hover) : {};

        const finalStyle = {
          ...(isDark ? baseStyleDark : baseStyle),
          ...(isHovered ? hoverStyle : {}),
        };

        return (
          <motion.button
            key={priority}
            type="button"
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05, type: "spring", stiffness: 300 }}
            whileHover={{ scale: disabled ? 1 : 1.02, y: -2 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            onHoverStart={() => !disabled && setHoveredPriority(priority)}
            onHoverEnd={() => setHoveredPriority(null)}
            onClick={() => !disabled && onChange(priority)}
            disabled={disabled}
            className={cn(
              "relative overflow-hidden rounded-xl px-3 py-3 transition-all duration-200",
              "flex flex-col items-center justify-center gap-1.5",
              "border-0",
              disabled && "opacity-50 cursor-not-allowed",
              !disabled && "cursor-pointer"
            )}
            style={finalStyle}
          >
            {/* Animated check icon for selected */}
            <AnimatePresence>
              {isSelected && (
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 180 }}
                  className="absolute top-1.5 right-1.5"
                >
                  <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Flag icon with animation */}
            <motion.div
              animate={
                isSelected
                  ? { rotate: [0, -10, 10, -10, 0], scale: [1, 1.1, 1] }
                  : isHovered
                  ? { scale: 1.1 }
                  : {}
              }
              transition={
                isSelected
                  ? { duration: 0.5, ease: "easeInOut" }
                  : { duration: 0.2 }
              }
            >
              <Flag
                className="w-5 h-5"
                style={{
                  opacity: isSelected ? 1 : 0.7,
                  color: isSelected ? 'currentColor' : 'currentColor',
                  fill: isSelected ? 'currentColor' : 'none'
                }}
                strokeWidth={2.5}
              />
            </motion.div>

            {/* Label */}
            <span className="text-xs font-bold uppercase tracking-wider">
              {styles.label}
            </span>

            {/* Description - only show on hover or selected */}
            <AnimatePresence>
              {(isHovered || isSelected) && (
                <motion.span
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                  className="text-[10px] font-medium opacity-90"
                >
                  {styles.description}
                </motion.span>
              )}
            </AnimatePresence>

            {/* Shine effect on hover */}
            {!disabled && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: isHovered ? 1 : 0 }}
                transition={{ duration: 0.2 }}
              />
            )}
          </motion.button>
        );
      })}
    </div>
  );
}
