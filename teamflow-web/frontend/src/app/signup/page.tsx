"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { apiClient } from "@/lib/api";

export default function SignupPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);

    const agencyData = {
      name: formData.get("agency_name") as string,
      email: formData.get("agency_email") as string,
    };

    const userData = {
      name: formData.get("user_name") as string,
      email: formData.get("user_email") as string,
      password: formData.get("password") as string,
      role: "admin",
    };

    try {
      const response = await apiClient.post("/api/v1/auth/signup", {
        agency_data: agencyData,
        user_data: userData,
      });

      // Store token and redirect
      const { access_token } = response.data;
      localStorage.setItem("auth_token", access_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-2xl font-bold mb-2">Create your agency</h1>
          <p className="text-gray-600 mb-6">
            Start managing your team's tasks with TeamFlow
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Agency Information */}
            <div>
              <label htmlFor="agency_name" className="block text-sm font-medium mb-1">
                Agency Name
              </label>
              <input
                type="text"
                id="agency_name"
                name="agency_name"
                required
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Creative Agency Inc."
              />
            </div>

            <div>
              <label htmlFor="agency_email" className="block text-sm font-medium mb-1">
                Agency Email
              </label>
              <input
                type="email"
                id="agency_email"
                name="agency_email"
                required
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="contact@agency.com"
              />
            </div>

            <hr className="my-4" />

            {/* Your Information */}
            <div>
              <label htmlFor="user_name" className="block text-sm font-medium mb-1">
                Your Name
              </label>
              <input
                type="text"
                id="user_name"
                name="user_name"
                required
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="user_email" className="block text-sm font-medium mb-1">
                Your Email
              </label>
              <input
                type="email"
                id="user_email"
                name="user_email"
                required
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="john@agency.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                minLength={8}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Creating account..." : "Create agency"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an agency?{" "}
            <Link href="/login" className="text-purple-600 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
