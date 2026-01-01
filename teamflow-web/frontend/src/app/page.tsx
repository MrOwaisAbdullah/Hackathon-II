"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-orange-50 via-white to-teal-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="z-10 max-w-2xl w-full text-center"
      >
        <div className="mb-6 flex justify-center">
          <div className="w-20 h-20 rounded-2xl bg-primary flex items-center justify-center shadow-lg">
            <span className="text-primary-foreground font-bold text-4xl">T</span>
          </div>
        </div>

        <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
          TeamFlow
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Task management CRM built for creative agencies
        </p>

        <div className="flex gap-4 justify-center">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              href="/signup"
              className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium inline-block"
            >
              Get Started
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              href="/login"
              className="px-6 py-3 border-2 border-primary text-primary rounded-lg hover:bg-primary/10 transition-colors font-medium inline-block"
            >
              Sign In
            </Link>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 grid grid-cols-3 gap-8 text-center"
        >
          <div>
            <p className="text-3xl font-bold text-foreground">10k+</p>
            <p className="text-sm text-muted-foreground">Active Users</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-foreground">500k+</p>
            <p className="text-sm text-muted-foreground">Tasks Completed</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-foreground">99.9%</p>
            <p className="text-sm text-muted-foreground">Uptime</p>
          </div>
        </motion.div>
      </motion.div>
    </main>
  );
}
