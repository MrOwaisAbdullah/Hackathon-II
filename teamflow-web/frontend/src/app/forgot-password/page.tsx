"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [email, setEmail] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Password reset API endpoint is not yet implemented.
      // To implement, add /api/auth/forgot-password endpoint to backend
      // that sends a reset email via SendGrid.
      // For now, simulate the API call for UI demonstration.
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Simulate success
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to send reset email");
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
        <div className="bg-zinc-900 rounded-2xl shadow-xl p-8 border border-zinc-800 relative overflow-hidden">
          {/* Ambient glow effect */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-lime-500/5 rounded-full blur-3xl pointer-events-none" />

          {/* Back button */}
          <Link
            href="/login"
            className="absolute top-6 left-6 text-zinc-400 hover:text-zinc-300 transition-colors flex items-center gap-2 text-sm relative z-10"
          >
            <ArrowLeft size={16} />
            Back to login
          </Link>

          <div className="mb-8 text-center relative z-10">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              className="w-12 h-12 rounded-xl bg-lime-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-lime-900/20"
            >
              <span className="text-black font-bold text-xl">T</span>
            </motion.div>
            <h1 className="text-2xl font-bold text-white mb-2">Forgot Password?</h1>
            <p className="text-zinc-400">
              {success
                ? "Check your email for reset instructions"
                : "Enter your email to receive a password reset link"}
            </p>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 p-3 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm font-medium relative z-10 flex items-start gap-2"
              >
                <AlertCircle size={16} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          {success ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-8 relative z-10"
            >
              <div className="w-16 h-16 rounded-full bg-lime-500/20 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-lime-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Reset Email Sent!
              </h3>
              <p className="text-zinc-400 text-sm mb-6">
                We've sent a password reset link to{" "}
                <span className="text-lime-400 font-medium">{email}</span>
              </p>
              <p className="text-zinc-500 text-xs mb-6">
                Didn't receive the email? Check your spam folder or request a new link.
              </p>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setSuccess(false);
                  setError(null);
                }}
                className="text-lime-400 hover:text-lime-300 text-sm font-medium transition-colors"
              >
                Try another email address
              </motion.button>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-1.5">
                  Email Address
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
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-11 pr-4 py-2.5 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
                    placeholder="you@company.com"
                  />
                </div>
                <p className="text-xs text-zinc-500 mt-2">
                  We'll send a password reset link to this email address.
                </p>
              </div>

              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full bg-lime-400 text-black py-2.5 rounded-lg hover:bg-lime-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-bold shadow-lg shadow-lime-900/20"
              >
                {loading ? "Sending..." : "Send Reset Link"}
              </motion.button>
            </form>
          )}

          <p className="mt-8 text-center text-sm text-zinc-500 relative z-10">
            Remember your password?{" "}
            <Link href="/login" className="text-lime-400 hover:text-lime-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>

        <div className="mt-6 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
          <p className="text-xs text-zinc-400 text-center">
            <strong className="text-lime-400">Note:</strong> Password reset links expire
            after 1 hour for security purposes.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
