/** Dashboard layout with sidebar. SSR-safe. */
'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Sidebar } from '@/components/dashboard/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Sidebar />
        <main style={{ marginLeft: 'var(--sidebar-width, 256px)', transition: 'margin-left 0.3s ease-in-out' }}>
          {children}
        </main>
      </div>
    </ProtectedRoute>
  );
}
