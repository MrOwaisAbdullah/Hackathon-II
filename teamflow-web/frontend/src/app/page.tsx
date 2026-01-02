"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-white text-zinc-950 relative overflow-hidden">
      
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-lime-200/30 rounded-full blur-[120px] pointer-events-none" />

      {/* Header / Nav */}
      <nav className="absolute top-0 left-0 right-0 p-6 flex justify-between items-center max-w-7xl mx-auto w-full z-20">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-lime-400 flex items-center justify-center">
            <span className="text-black font-bold text-lg">T</span>
          </div>
          <span className="font-bold text-xl tracking-tight">TeamFlow</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-lime-600 transition-colors">
            Sign In
          </Link>
          <Link href="/signup" className="px-4 py-2 bg-black text-white text-sm font-medium rounded-lg hover:bg-zinc-800 transition-colors">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="z-10 max-w-4xl w-full text-center mt-12"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-200 bg-white shadow-sm mb-8">
          <div className="w-2 h-2 rounded-full bg-lime-500 animate-pulse" />
          <span className="text-xs font-semibold text-zinc-600 uppercase tracking-wider">Intelligent Task Management</span>
        </div>

        <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 leading-[0.9]">
          SIMPLIFY YOUR <br />
          <span className="relative inline-block">
            WORKFLOW.
            <span className="absolute -bottom-2 left-0 right-0 h-4 bg-lime-300 -z-10 -rotate-1 rounded-full opacity-60" />
          </span>
        </h1>
        
        <p className="text-xl text-zinc-500 mb-10 max-w-2xl mx-auto leading-relaxed">
          TeamFlow helps you <strong className="text-black">think less</strong>, plan smarter, and execute faster. 
          The agency operating system for high-performance teams.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              href="/signup"
              className="px-8 py-4 bg-black text-white rounded-xl hover:bg-zinc-800 transition-all font-bold text-lg shadow-xl shadow-zinc-200"
            >
              Start Free Trial →
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              href="/login"
              className="px-8 py-4 bg-white text-black border border-zinc-200 rounded-xl hover:border-zinc-300 hover:bg-zinc-50 transition-all font-bold text-lg"
            >
              Sign In
            </Link>
          </motion.div>
        </div>

        {/* Stats / Social Proof */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-16 border-t border-zinc-100 pt-12"
        >
          <div>
            <p className="text-4xl font-black text-zinc-300">50+</p>
            <p className="text-sm font-medium text-zinc-400 uppercase tracking-wide mt-1">Agencies</p>
          </div>
          <div>
            <p className="text-4xl font-black text-zinc-300">95%</p>
            <p className="text-sm font-medium text-zinc-400 uppercase tracking-wide mt-1">Efficiency</p>
          </div>
          <div>
            <p className="text-4xl font-black text-zinc-300">10k+</p>
            <p className="text-sm font-medium text-zinc-400 uppercase tracking-wide mt-1">Tasks Done</p>
          </div>
          <div>
            <p className="text-4xl font-black text-zinc-300">24/7</p>
            <p className="text-sm font-medium text-zinc-400 uppercase tracking-wide mt-1">Support</p>
          </div>
        </motion.div>
      </motion.div>
    </main>
  );
}