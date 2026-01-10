'use client';

import { usePathname } from 'next/navigation';
import { ChatWidget } from './ChatWidget';

/**
 * ChatWidgetWrapper - Client component that conditionally renders ChatWidget
 *
 * Hides the floating chat widget on the fullscreen /chat page to avoid duplication.
 */
export function ChatWidgetWrapper() {
  const pathname = usePathname();

  // Don't show floating widget on fullscreen chat page
  if (pathname === '/chat') {
    return null;
  }

  return (
    <ChatWidget
      apiUrl={process.env.NEXT_PUBLIC_API_URL}
      position="bottom-right"
    />
  );
}
