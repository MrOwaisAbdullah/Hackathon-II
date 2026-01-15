"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { Eye, EyeOff, Mail } from "lucide-react";

// Password input with visibility toggle (reusable component)
const PasswordInput = ({
  id,
  name,
  value,
  onChange,
  placeholder,
  label,
  required = true,
}: {
  id: string;
  name: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  label: string;
  required?: boolean;
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label htmlFor={id} className="block text-sm font-medium text-zinc-300">
          {label}
        </label>
        <Link
          href="/forgot-password"
          className="text-xs text-lime-400 hover:text-lime-300 transition-colors"
        >
          Forgot password?
        </Link>
      </div>
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          id={id}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          className="w-full px-4 py-2.5 pr-12 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
          placeholder={placeholder}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 -mt-px text-zinc-500 hover:text-zinc-300 transition-colors flex items-center justify-center"
          aria-label={showPassword ? "Hide password" : "Show password"}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  );
};

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const response = await api.post<{
        access_token: string;
        user: Record<string, unknown>;
      }>("/api/v1/auth/login", {
        email,
        password,
      });

      // Store token and redirect
      localStorage.setItem("auth_token", response.data.access_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-zinc-900 rounded-2xl shadow-xl p-8 border border-zinc-800 relative overflow-hidden">
          {/* Ambient glow effect */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-lime-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="mb-8 text-center relative z-10">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              className="w-12 h-12 rounded-xl bg-lime-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-lime-900/20"
            >
              <span className="text-black font-bold text-xl">T</span>
            </motion.div>
            <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-zinc-400">Sign in to your TeamFlow workspace</p>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 p-3 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm font-medium relative z-10"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-1.5">
                Email
              </label>
              <div className="relative">
                <Mail
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
                  size={18}
                />
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  className="w-full pl-11 pr-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                  placeholder="you@company.com"
                />
              </div>
            </div>

            <PasswordInput
              id="password"
              name="password"
              placeholder="••••••••"
              label="Password"
            />

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-lime-400 text-black py-2.5 rounded-lg hover:bg-lime-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-bold shadow-lg shadow-lime-900/20"
            >
              {loading ? "Signing in..." : "Sign In"}
            </motion.button>
          </form>

          <p className="mt-8 text-center text-sm text-zinc-500 relative z-10">
            Don't have an account?{" "}
            <Link href="/signup" className="text-lime-400 hover:text-lime-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>

        <div className="mt-6 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 text-center">
          <p className="text-xs font-bold text-lime-400 uppercase tracking-widest mb-1">
            Test Credentials
          </p>
          <p className="text-sm text-zinc-300">
            <span className="text-zinc-500">Email:</span> admin@test.com <br />
            <span className="text-zinc-500">Pass:</span> password123
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-zinc-600">
          Secure enterprise-grade task management
        </p>
      </motion.div>
    </div>
  );
}
