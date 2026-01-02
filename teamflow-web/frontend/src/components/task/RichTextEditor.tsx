"use client";

/** RichTextEditor - Markdown-based rich text editor.
 *
 * Task T144 (US6): Rich text editor with:
 * - Markdown support for formatting
 * - Live preview
 * - Toolbar with formatting buttons
 * - Auto-expanding textarea
 */

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Bold,
  Italic,
  List,
  Heading1,
  Heading2,
  Link,
  Minus,
} from "lucide-react";

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
  const [isPreview, setIsPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [selectionRange, setSelectionRange] = useState<{
    start: number;
    end: number;
  } | null>(null);

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
        className="flex items-center gap-1 p-1 bg-muted/30 border border-border rounded-t-lg flex-wrap"
      >
        {toolbarButtons.map((button) => (
          <motion.button
            key={button.label}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={button.action}
            disabled={disabled}
            className={`
              p-2 rounded hover:bg-muted/50 transition-colors
              ${disabled ? "opacity-50 cursor-not-allowed" : ""}
            `}
            title={`${button.label} (${button.shortcut})`}
            aria-label={button.label}
          >
            <button.icon className="w-4 h-4 text-muted-foreground" />
          </motion.button>
        ))}

        <div className="flex-1" />

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsPreview(!isPreview)}
          className="px-3 py-1 text-sm rounded hover:bg-muted/50 transition-colors"
          aria-label={isPreview ? "Edit mode" : "Preview mode"}
          aria-pressed={isPreview}
        >
          {isPreview ? "Edit" : "Preview"}
        </motion.button>
      </motion.div>

      {/* Editor / Preview */}
      <div className="relative min-h-[120px] border border-t-0 border-border rounded-b-lg bg-card">
        {isPreview ? (
          // Markdown Preview
          <div className="p-3 prose prose-sm dark:prose-invert max-w-none">
            {value ? (
              <div
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(value),
                }}
              />
            ) : (
              <p className="text-muted-foreground italic">Empty preview</p>
            )}
          </div>
        ) : (
          // Textarea
          <textarea
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
      </div>
    </div>
  );
}

// Simple markdown renderer (for preview)
function renderMarkdown(markdown: string): string {
  let html = markdown
    // Escape HTML
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")

    // Headers
    .replace(/^### (.*$)/gim, "<h3>$1</h3>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/^# (.*$)/gim, "<h1>$1</h1>")

    // Bold
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")

    // Italic
    .replace(/\*(.*?)\*/g, "<em>$1</em>")

    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')

    // Lists
    .replace(/^\- (.*$)/gim, "<li>$1</li>")

    // Horizontal rules
    .replace(/^---$/gim, "<hr>")

    // Line breaks
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>");

  // Wrap list items
  if (html.includes("<li>")) {
    html = html.replace(/(<li>.*<\/li>)/g, "<ul>$1</ul>");
  }

  return `<p>${html}</p>`;
}
