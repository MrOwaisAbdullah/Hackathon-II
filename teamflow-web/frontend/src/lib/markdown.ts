/**
 * Simple markdown renderer for task descriptions and notes.
 * Supports: headers, bold, italic, links, lists, horizontal rules.
 */

export function renderMarkdown(markdown: string): string {
  if (!markdown) return "";

  let html = markdown
    // Escape HTML first
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")

    // Headers
    .replace(/^### (.*$)/gim, '<h3 class="text-sm font-bold mt-2 mb-1">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-base font-bold mt-2 mb-1">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-lg font-bold mt-2 mb-1">$1</h1>')

    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')

    // Italic
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')

    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener" class="text-accent hover:underline">$1</a>')

    // Lists
    .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')

    // Code (inline)
    .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-muted rounded text-xs font-mono">$1</code>')

    // Horizontal rules
    .replace(/^---$/gim, '<hr class="my-2 border-border" />')

    // Line breaks
    .replace(/\n\n/g, '</p><p class="my-1">')
    .replace(/\n/g, '<br />');

  // Wrap list items in ul tags
  if (html.includes("<li>")) {
    html = html.replace(/(<li>.*<\/li>)/g, '<ul class="my-1 ml-4">$1</ul>');
  }

  return `<p class="my-0">${html}</p>`;
}
