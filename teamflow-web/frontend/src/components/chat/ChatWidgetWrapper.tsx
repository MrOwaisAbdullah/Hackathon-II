'use client';

import { usePathname } from 'next/navigation';
import { ChatWidget } from './ChatWidget';

/**
 * ChatWidgetWrapper - Client component that conditionally renders ChatWidget
 *
 * Restricts the floating chat widget to authenticated dashboard routes only.
 *
 * Dashboard routes where widget IS shown:
 * - /dashboard
 * - /tasks
 * - /projects
 * - /time-entries
 * - /team
 * - /settings
 * - /archive
 *
 * Routes where widget is NOT shown:
 * - Public pages: /, /contact, /about, /privacy
 * - Auth pages: /login, /signup
 * - Fullscreen chat: /chat (has its own fullscreen ChatWidget)
 */
const DASHBOARD_ROUTES = [
  '/dashboard',
  '/tasks',
  '/projects',
  '/time-entries',
  '/team',
  '/settings',
  '/archive',
] as const;

export function ChatWidgetWrapper() {
  const pathname = usePathname();

  // Check if current route is a dashboard route
  // Exact match or starts with route + '/' (for sub-routes like /projects/123)
  const isDashboardRoute = DASHBOARD_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  );

  // Don't show floating widget on non-dashboard routes
  if (!isDashboardRoute) {
    return null;
  }

  return (
    <ChatWidget
      apiUrl={process.env.NEXT_PUBLIC_API_URL}
      position="bottom-right"
    />
  );
}
