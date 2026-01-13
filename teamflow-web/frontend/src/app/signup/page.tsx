"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useState, useMemo } from "react";
import { api } from "@/lib/api";
import { Eye, EyeOff, Check, X, Shield, AlertTriangle } from "lucide-react";

// Password strength levels
type PasswordStrength = "weak" | "medium" | "strong";

interface StrengthResult {
  strength: PasswordStrength;
  score: number; // 0-3
  feedback: string[];
}

// Password strength calculator
const calculatePasswordStrength = (password: string): StrengthResult => {
  const feedback: string[] = [];
  let score = 0;

  if (!password) {
    return { strength: "weak", score: 0, feedback: [] };
  }

  // Length check
  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push("At least 8 characters");
  }

  // Complexity checks
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push("Upper & lower case letters");
  }

  if (/[0-9]/.test(password)) {
    score += 1;
  } else {
    feedback.push("At least one number");
  }

  if (/[^a-zA-Z0-9]/.test(password)) {
    score += 1;
  } else {
    feedback.push("Special character (!@#$%)");
  }

  // Map score to strength level
  let strength: PasswordStrength = "weak";
  if (score >= 3) strength = "medium";
  if (score === 4) strength = "strong";

  return { strength, score, feedback };
};

// Strength meter component
const PasswordStrengthMeter = ({ password }: { password: string }) => {
  const { strength, score, feedback } = useMemo(
    () => calculatePasswordStrength(password),
    [password]
  );

  if (!password) return null;

  // Color mapping
  const colors = {
    weak: "bg-red-500",
    medium: "bg-yellow-500",
    strong: "bg-lime-500",
  };

  const glowColors = {
    weak: "shadow-red-500/50",
    medium: "shadow-yellow-500/50",
    strong: "shadow-lime-500/50",
  };

  const width = `${(score / 4) * 100}%`;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mt-3"
    >
      {/* Progress bar */}
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden mb-2">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className={`h-full ${colors[strength]} ${glowColors[strength]} shadow-lg`}
        />
      </div>

      {/* Strength label and feedback */}
      <div className="flex items-start gap-2">
        {strength === "strong" && <Check className="w-4 h-4 text-lime-400 mt-0.5" />}
        {strength === "medium" && <Shield className="w-4 h-4 text-yellow-400 mt-0.5" />}
        {strength === "weak" && <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5" />}

        <div className="flex-1">
          <p
            className={`text-xs font-medium capitalize ${
              strength === "strong"
                ? "text-lime-400"
                : strength === "medium"
                ? "text-yellow-400"
                : "text-red-400"
            }`}
          >
            Password strength: {strength}
          </p>
          {feedback.length > 0 && (
            <motion.ul
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xs text-zinc-500 mt-1 space-y-0.5"
            >
              {feedback.map((item, i) => (
                <li key={i} className="flex items-center gap-1.5">
                  <X className="w-3 h-3" />
                  {item}
                </li>
              ))}
            </motion.ul>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Password input with visibility toggle
const PasswordInput = ({
  id,
  name,
  value,
  onChange,
  placeholder,
  showStrength = false,
  label,
}: {
  id: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  showStrength?: boolean;
  label: string;
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-zinc-300 mb-1.5">
        {label}
      </label>
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          id={id}
          name={name}
          value={value}
          onChange={onChange}
          required
          minLength={8}
          className="w-full px-4 py-2.5 pr-12 border border-zinc-700 bg-zinc-950/50 rounded-lg focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400 text-white placeholder:text-zinc-600 transition-all outline-none"
          placeholder={placeholder}
        />
        <motion.button
          type="button"
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </motion.button>
      </div>
      {showStrength && <PasswordStrengthMeter password={value} />}
    </div>
  );
};

// Password match indicator
const PasswordMatchIndicator = ({ password, confirmPassword }: { password: string; confirmPassword: string }) => {
  if (!confirmPassword) return null;

  const isMatch = password === confirmPassword && password.length > 0;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -10 }}
        className={`flex items-center gap-2 text-xs mt-2 ${
          isMatch ? "text-lime-400" : "text-red-400"
        }`}
      >
        {isMatch ? <Check size={14} /> : <X size={14} />}
        <span>{isMatch ? "Passwords match" : "Passwords do not match"}</span>
      </motion.div>
    </AnimatePresence>
  );
};

export default function SignupPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setFormError(null);

    // Validate passwords match
    if (password !== confirmPassword) {
      setFormError("Passwords do not match");
      setLoading(false);
      return;
    }

    // Validate password strength
    const { score } = calculatePasswordStrength(password);
    if (score < 2) {
      setFormError("Password is too weak. Please add more complexity.");
      setLoading(false);
      return;
    }

    const formData = new FormData(e.currentTarget);

    const agencyData = {
      name: formData.get("agency_name") as string,
      email: formData.get("agency_email") as string,
    };

    const userData = {
      name: formData.get("user_name") as string,
      email: formData.get("agency_email") as string, // Use agency email for user too
      password: password,
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
            <h1 className="text-2xl font-bold text-white mb-2">Start Your Trial</h1>
            <p className="text-zinc-400">
              Join thousands of agencies managing tasks with TeamFlow
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm font-medium"
            >
              {error}
            </motion.div>
          )}

          {formError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm font-medium"
            >
              {formError}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
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
              <span className="bg-zinc-900 px-3 text-xs text-zinc-500 uppercase tracking-widest -mt-3">
                Admin Details
              </span>
            </div>

            {/* Your Information */}
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

            {/* Password field with strength indicator */}
            <PasswordInput
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              showStrength={true}
              label="Password"
            />

            {/* Confirm password field */}
            <div>
              <PasswordInput
                id="confirm_password"
                name="confirm_password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                showStrength={false}
                label="Confirm Password"
              />
              <PasswordMatchIndicator password={password} confirmPassword={confirmPassword} />
            </div>

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

          <p className="mt-8 text-center text-sm text-zinc-500 relative z-10">
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
