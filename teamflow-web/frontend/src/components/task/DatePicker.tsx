"use client";

/** DatePicker - Date picker component for task due dates.
 *
 * Task T146 (US6): Date picker component with:
 * - Calendar popover for date selection
 * - Clear button to remove due date
 * - Formatted date display
 * - Month/Year navigation
 * - Accessibility support
 */

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Calendar, X, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  value?: string;
  onChange: (date: string | undefined) => void;
  disabled?: boolean;
  className?: string;
}

// Helper to generate calendar days
function generateCalendarDays(year: number, month: number): (number | null)[] {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days: (number | null)[] = [];

  // Add null placeholders for days before the first of the month
  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }

  // Add actual days
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day);
  }

  return days;
}

export function DatePicker({ value, onChange, disabled = false, className = "" }: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [viewYear, setViewYear] = useState(new Date().getFullYear());
  const [viewMonth, setViewMonth] = useState(new Date().getMonth());

  // Update view when a value is selected
  const selectedDate = useMemo(() => {
    if (value) return new Date(value);
    return null;
  }, [value]);

  // Sync view with selected date when opening
  const handleOpen = () => {
    if (selectedDate) {
      setViewYear(selectedDate.getFullYear());
      setViewMonth(selectedDate.getMonth());
    }
    setIsOpen(true);
  };

  const calendarDays = useMemo(() => generateCalendarDays(viewYear, viewMonth), [viewYear, viewMonth]);

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const handleDateSelect = (day: number) => {
    const newDate = new Date(viewYear, viewMonth, day);
    onChange(newDate.toISOString().split('T')[0]);
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(undefined);
  };

  const handlePreviousMonth = () => {
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear(viewYear - 1);
    } else {
      setViewMonth(viewMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear(viewYear + 1);
    } else {
      setViewMonth(viewMonth + 1);
    }
  };

  return (
    <div className={cn("relative", className)} data-testid="date-picker">
      {/* Trigger Button */}
      <motion.button
        type="button"
        whileHover={{ scale: disabled ? 1 : 1.01 }}
        whileTap={{ scale: disabled ? 1 : 0.99 }}
        onClick={() => !disabled && (isOpen ? setIsOpen(false) : handleOpen())}
        disabled={disabled}
        className={cn(
          "w-full flex items-center justify-between gap-3 px-4 py-3",
          "border-2 rounded-xl bg-background transition-all duration-200",
          "focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent",
          disabled ? "opacity-50 cursor-not-allowed border-input" : "border-input hover:border-input/80 cursor-pointer"
        )}
        aria-label={value ? `Change date: ${new Date(value).toLocaleDateString()}` : "Select due date"}
        data-testid="date-trigger"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
            <Calendar className="w-4 h-4 text-accent" />
          </div>
          <span className="text-sm font-medium text-foreground">
            {value
              ? new Date(value).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })
              : "No due date"}
          </span>
        </div>
        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="p-1 rounded-lg hover:bg-muted transition-colors"
            aria-label="Clear due date"
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        )}
      </motion.button>

      {/* Calendar Popover */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
              aria-hidden="true"
            />

            {/* Calendar */}
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full right-0 mt-2 w-80 bg-card border border-input rounded-xl shadow-xl z-20 overflow-hidden"
              data-testid="calendar-popover"
            >
              {/* Header with Navigation */}
              <div className="flex items-center justify-between p-4 border-b border-input bg-muted/30">
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handlePreviousMonth}
                  className="p-1 rounded-lg hover:bg-accent/10 transition-colors"
                  aria-label="Previous month"
                >
                  <ChevronLeft className="w-4 h-4 text-accent" />
                </motion.button>

                <span className="font-semibold text-sm text-foreground">
                  {monthNames[viewMonth]} {viewYear}
                </span>

                <motion.button
                  type="button"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleNextMonth}
                  className="p-1 rounded-lg hover:bg-accent/10 transition-colors"
                  aria-label="Next month"
                >
                  <ChevronRight className="w-4 h-4 text-accent" />
                </motion.button>
              </div>

              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-1 p-3 bg-background">
                {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day) => (
                  <div
                    key={day}
                    className="text-center text-xs text-muted-foreground font-medium py-2"
                  >
                    {day}
                  </div>
                ))}

                {/* Calendar Days */}
                {calendarDays.map((day, index) => {
                  const isSelected =
                    day &&
                    selectedDate &&
                    selectedDate.getDate() === day &&
                    selectedDate.getMonth() === viewMonth &&
                    selectedDate.getFullYear() === viewYear;

                  const isToday =
                    day &&
                    new Date().getDate() === day &&
                    new Date().getMonth() === viewMonth &&
                    new Date().getFullYear() === viewYear;

                  return (
                    <button
                      key={index}
                      type="button"
                      onClick={() => day && handleDateSelect(day)}
                      disabled={!day}
                      className={cn(
                        "aspect-square flex items-center justify-center",
                        "text-sm rounded-lg transition-all duration-200",
                        day
                          ? "hover:bg-accent/10 cursor-pointer"
                          : "cursor-default"
                        ,
                        isSelected && "bg-accent text-accent-foreground font-semibold shadow-md",
                        isToday && !isSelected && "border-2 border-accent text-accent"
                      )}
                      aria-label={day ? `${monthNames[viewMonth]} ${day}, ${viewYear}` : ""}
                      aria-pressed={isSelected}
                    >
                      {day || ""}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
