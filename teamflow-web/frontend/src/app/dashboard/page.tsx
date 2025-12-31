"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold text-purple-600">TeamFlow</h1>
            <button
              onClick={() => {
                localStorage.removeItem("auth_token");
                window.location.href = "/login";
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Sign out
            </button>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-2">Dashboard</h2>
            <p className="text-gray-600">Welcome to your agency workspace</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500 mb-1">Total Projects</p>
              <p className="text-3xl font-bold">0</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500 mb-1">Total Tasks</p>
              <p className="text-3xl font-bold">0</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500 mb-1">Team Members</p>
              <p className="text-3xl font-bold">0</p>
            </div>
          </div>

          <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
            <p className="text-gray-500">
              Task board coming soon...
            </p>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
