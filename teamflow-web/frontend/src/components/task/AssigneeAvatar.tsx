"use client";

import { motion } from "framer-motion";

interface AssigneeAvatarProps {
  name?: string;
  email?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "w-5 h-5 text-[10px]",
  md: "w-7 h-7 text-xs",
  lg: "w-10 h-10 text-sm",
};

/**
 * AssigneeAvatar - Displays a user avatar with initials
 *
 * Shows a gradient circle with user initials when name is provided,
 * or a placeholder ring when unassigned.
 */
export function AssigneeAvatar({
  name,
  email,
  size = "sm",
  className = "",
}: AssigneeAvatarProps) {
  // Get initials from name (first letter of each word, max 2)
  const initials = name
    ? name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : null;

  // Get first letter of email as fallback
  const emailInitial = email ? email[0].toUpperCase() : null;

  // Generate consistent color based on name/email
  const getColorIndex = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return Math.abs(hash % 6);
  };

  const colorClass = name || email
    ? [
        "from-blue-500 to-blue-600",
        "from-purple-500 to-purple-600",
        "from-green-500 to-green-600",
        "from-amber-500 to-amber-600",
        "from-rose-500 to-rose-600",
        "from-cyan-500 to-cyan-600",
      ][getColorIndex(name || email || '')]
    : "";

  if (!name && !email) {
    // Unassigned placeholder
    return (
      <div
        className={`${sizeClasses[size]} rounded-full border-2 border-dashed border-muted-foreground/30 ${className}`}
        title="Unassigned"
      />
    );
  }

  return (
    <motion.div
      whileHover={{ scale: 1.1 }}
      className={`${sizeClasses[size]} rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center text-white font-medium ${className}`}
      title={name || email}
    >
      {initials || emailInitial || "?"}
    </motion.div>
  );
}
