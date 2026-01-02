"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";

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
      const response = await api.post("/api/v1/auth/register", {
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
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-zinc-900 rounded-2xl shadow-xl p-8 border border-zinc-800">
          <div className="mb-8 text-center">
            <div className="w-12 h-12 rounded-xl bg-lime-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-lime-900/20">
              <span className="text-black font-bold text-xl">T</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Start Your Trial</h1>
            <p className="text-zinc-400">
              Join thousands of agencies managing tasks with TeamFlow
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Agency Information */}
            <div>
              <label htmlFor="agency_name" className="block text-sm font-medium text-zinc-300 mb-1.5">
                Agency Name
              </label>
              <input
                type="text"
                id="agency_name"
                name="agency_name"
                required
                className="w-full px-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                placeholder="Acme Creative"
              />
            </div>

            <div>
              <label htmlFor="agency_email" className="block text-sm font-medium text-zinc-300 mb-1.5">
                Work Email
              </label>
              <input
                type="email"
                id="agency_email"
                name="agency_email"
                required
                className="w-full px-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                placeholder="team@acme.com"
              />
            </div>

            <div className="border-t border-zinc-800 my-6 flex items-center justify-center">
              <span className="bg-zinc-900 px-3 text-xs text-zinc-500 uppercase tracking-widest -mt-3">Admin Details</span>
            </div>

            {/* Your Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="user_name" className="block text-sm font-medium text-zinc-300 mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  id="user_name"
                  name="user_name"
                  required
                  className="w-full px-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-zinc-300 mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  minLength={8}
                  className="w-full px-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Hidden field for user email (same as agency for simplicity or separate if needed) */}
            <input type="hidden" name="user_email" value="admin@placeholder.com" /> {/* Ideally JS sets this to match agency email */}

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-lime-400 text-black py-2.5 rounded-lg hover:bg-lime-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-bold shadow-lg shadow-lime-900/20 mt-2"
            >
              {loading ? "Setting up..." : "Create Workspace"}
            </motion.button>
          </form>

          <p className="mt-8 text-center text-sm text-zinc-500">
            Already have an account?{" "}
            <Link href="/login" className="text-lime-400 hover:text-lime-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}