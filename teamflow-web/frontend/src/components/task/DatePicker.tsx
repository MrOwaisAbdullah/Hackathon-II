"use client";

/** DatePicker - Date picker component for task due dates.
 *
 * Task T146 (US6): Date picker component with:
 * - Calendar popover for date selection
 * - Clear button to remove due date
 * - Formatted date display
 * - Accessibility support
 */

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Calendar, X } from "lucide-react";

interface DatePickerProps {
  value?: string;
  onChange: (date: string | undefined) => void;
  disabled?: boolean;
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

export function DatePicker({ value, onChange, disabled = false }: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const currentDate = useMemo(() => {
    if (value) return new Date(value);
    return new Date();
  }, [value]);

  const viewDate = currentDate;
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const calendarDays = useMemo(() => generateCalendarDays(year, month), [year, month]);

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const handleDateSelect = (day: number) => {
    const newDate = new Date(year, month, day);
    onChange(newDate.toISOString().split('T')[0]);
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(undefined);
  };

  return (
    <div className="relative" data-testid="date-picker">
      {/* Trigger Button */}
      <motion.button
        whileHover={{ scale: disabled ? 1 : 1.01 }}
        whileTap={{ scale: disabled ? 1 : 0.99 }}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full flex items-center justify-between gap-2 px-3 py-2
          border border-border rounded-lg bg-muted/30
          transition-colors
          ${disabled ? "opacity-50 cursor-not-allowed" : "hover:bg-muted/50"}
        `}
        aria-label={value ? `Change date: ${new Date(value).toLocaleDateString()}` : "Select due date"}
        data-testid="date-trigger"
      >
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm">
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
            onClick={handleClear}
            className="p-1 rounded hover:bg-muted"
            aria-label="Clear due date"
          >
            <X className="w-3 h-3 text-muted-foreground" />
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
              className="absolute top-full right-0 mt-2 w-72 bg-card border border-border rounded-lg shadow-lg z-20"
              data-testid="calendar-popover"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-3 border-b border-border">
                <span className="font-semibold text-sm">
                  {monthNames[month]} {year}
                </span>
              </div>

              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-1 p-2">
                {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day) => (
                  <div
                    key={day}
                    className="text-center text-xs text-muted-foreground font-medium py-1"
                  >
                    {day}
                  </div>
                ))}

                {/* Calendar Days */}
                {calendarDays.map((day, index) => {
                  const isSelected =
                    day &&
                    value &&
                    new Date(value).getDate() === day &&
                    new Date(value).getMonth() === month &&
                    new Date(value).getFullYear() === year;

                  const isToday =
                    day &&
                    new Date().getDate() === day &&
                    new Date().getMonth() === month &&
                    new Date().getFullYear() === year;

                  return (
                    <button
                      key={index}
                      onClick={() => day && handleDateSelect(day)}
                      disabled={!day}
                      className={`
                        calendar-day aspect-square flex items-center justify-center
                        text-sm rounded-md transition-colors
                        ${day
                          ? "hover:bg-muted/50 cursor-pointer"
                          : "cursor-default"
                        }
                        ${isSelected
                          ? "bg-primary text-primary-foreground font-semibold"
                          : ""
                        }
                        ${isToday && !isSelected
                          ? "border border-primary text-primary"
                          : ""
                        }
                      `}
                      aria-label={day ? `${monthNames[month]} ${day}` : ""}
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
