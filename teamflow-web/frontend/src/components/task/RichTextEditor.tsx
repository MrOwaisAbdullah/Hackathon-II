"use client";

/** RichTextEditor - Markdown-based rich text editor.
 *
 * Task T144 (US6): Rich text editor with:
 * - Markdown support for formatting
 * - Toolbar with formatting buttons
 * - Auto-expanding textarea
 * - Preview mode toggle
 */

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bold,
  Italic,
  List,
  Heading1,
  Heading2,
  Link,
  Minus,
  Eye,
  Edit,
} from "lucide-react";
import { renderMarkdown } from "@/lib/markdown";

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

// Markdown formatting helpers
const insertMarkdown = (
  text: string,
  selectionStart: number,
  selectionEnd: number,
  prefix: string,
  suffix: string = prefix
): { text: string; newPosition: number } => {
  const before = text.substring(0, selectionStart);
  const selected = text.substring(selectionStart, selectionEnd);
  const after = text.substring(selectionEnd);

  const newText = `${before}${prefix}${selected}${suffix}${after}`;
  const newPosition = selectionStart + prefix.length + selected.length + suffix.length;

  return { text: newText, newPosition };
};

export function RichTextEditor({
  value,
  onChange,
  placeholder = "Add a description...",
  disabled = false,
}: RichTextEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [selectionRange, setSelectionRange] = useState<{
    start: number;
    end: number;
  } | null>(null);
  const [isPreview, setIsPreview] = useState(false);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [value]);

  // Handle formatting button clicks
  const handleFormat = (prefix: string, suffix?: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = selectionRange?.start ?? textarea.selectionStart;
    const end = selectionRange?.end ?? textarea.selectionEnd;

    const result = insertMarkdown(value, start, end, prefix, suffix);
    onChange(result.text);

    // Restore cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(result.newPosition, result.newPosition);
      setSelectionRange(null);
    }, 0);
  };

  const handleSelectionChange = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      setSelectionRange({
        start: textarea.selectionStart,
        end: textarea.selectionEnd,
      });
    }
  };

  const toolbarButtons = [
    {
      icon: Heading1,
      label: "Heading 1",
      action: () => handleFormat("# ", ""),
      shortcut: "Ctrl+Alt+1",
    },
    {
      icon: Heading2,
      label: "Heading 2",
      action: () => handleFormat("## ", ""),
      shortcut: "Ctrl+Alt+2",
    },
    {
      icon: Bold,
      label: "Bold",
      action: () => handleFormat("**", "**"),
      shortcut: "Ctrl+B",
    },
    {
      icon: Italic,
      label: "Italic",
      action: () => handleFormat("*", "*"),
      shortcut: "Ctrl+I",
    },
    {
      icon: List,
      label: "List",
      action: () => handleFormat("- ", ""),
      shortcut: "Ctrl+L",
    },
    {
      icon: Minus,
      label: "Horizontal Rule",
      action: () => handleFormat("\n---\n", ""),
    },
    {
      icon: Link,
      label: "Link",
      action: () => handleFormat("[", "](url)"),
      shortcut: "Ctrl+K",
    },
  ];

  return (
    <div className="space-y-2" data-testid="rich-text-editor">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between gap-1 p-1 bg-muted/30 border border-border rounded-t-lg"
      >
        <div className="flex items-center gap-1 flex-wrap">
          {toolbarButtons.map((button) => (
            <motion.button
              key={button.label}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={button.action}
              disabled={disabled || isPreview}
              type="button"
              className={`
                p-2 rounded hover:bg-muted/50 transition-colors
                ${(disabled || isPreview) ? "opacity-50 cursor-not-allowed" : ""}
              `}
              title={`${button.label} (${button.shortcut})`}
              aria-label={button.label}
            >
              <button.icon className="w-4 h-4 text-muted-foreground" />
            </motion.button>
          ))}
        </div>

        {/* Preview Toggle Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsPreview(!isPreview)}
          disabled={disabled}
          type="button"
          className={`
            flex items-center gap-1.5 px-2 py-1.5 rounded-md text-xs font-medium transition-colors
            ${isPreview
              ? "bg-accent text-accent-foreground"
              : "bg-muted/50 text-muted-foreground hover:bg-muted"
            }
            ${disabled ? "opacity-50 cursor-not-allowed" : ""}
          `}
          title={isPreview ? "Switch to edit mode" : "Switch to preview mode"}
        >
          {isPreview ? (
            <>
              <Edit className="w-3.5 h-3.5" />
              Edit
            </>
          ) : (
            <>
              <Eye className="w-3.5 h-3.5" />
              Preview
            </>
          )}
        </motion.button>
      </motion.div>

      {/* Editor / Preview */}
      <div className="relative min-h-[120px] border border-t-0 border-border rounded-b-lg bg-card">
        <AnimatePresence mode="wait">
          {isPreview ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-3 prose prose-sm max-w-none dark:prose-invert"
              dangerouslySetInnerHTML={{
                __html: renderMarkdown(value) || '<p class="text-muted-foreground italic">Nothing to preview</p>',
              }}
            />
          ) : (
            <motion.textarea
              key="editor"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onSelect={handleSelectionChange}
              onKeyUp={handleSelectionChange}
              disabled={disabled}
              placeholder={placeholder}
              className={`
                w-full min-h-[120px] p-3 bg-transparent resize-none
                focus:outline-none text-sm
                ${disabled ? "opacity-50 cursor-not-allowed" : ""}
              `}
              aria-label="Task description"
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
