"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

/**
 * MarketingHeader - Consistent header for all marketing/landing pages
 *
 * Used on: Home, Pricing, Privacy, Terms, Contact
 * NOT used on: Dashboard pages (which have their own layout)
 */
export function MarketingHeader() {
  return (
    <nav className="fixed top-0 left-0 right-0 px-4 sm:px-6 py-4 flex justify-between items-center max-w-7xl mx-auto w-full z-50 backdrop-blur-sm">
      <Link href="/" className="flex items-center gap-2">
        <motion.div
          whileHover={{ scale: 1.05, rotate: 5 }}
          className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-lime-400 flex items-center justify-center shadow-lg shadow-lime-400/20"
        >
          <span className="text-black font-black text-lg sm:text-xl tracking-tighter">T</span>
        </motion.div>
        <span className="font-bold text-base sm:text-xl tracking-tight">TeamFlow</span>
      </Link>

      <div className="flex items-center gap-2 sm:gap-6">
        <div className="hidden md:flex gap-6 text-sm font-medium text-zinc-400">
          <Link href="/#features" className="hover:text-white transition-colors">
            Features
          </Link>
          <Link href="/pricing" className="hover:text-white transition-colors">
            Pricing
          </Link>
          <Link href="/contact" className="hover:text-white transition-colors">
            Contact
          </Link>
        </div>
        <Link href="/login" className="hidden sm:block hover:text-white transition-colors text-sm font-medium text-zinc-400">
          Sign In
        </Link>
        <Link
          href="/signup"
          className="px-4 py-2 sm:px-5 sm:py-2.5 bg-lime-400 text-black text-xs sm:text-sm font-bold rounded-lg hover:bg-lime-300 transition-colors shadow-lg shadow-lime-400/20 flex items-center gap-1 sm:gap-2"
        >
          <span className="hidden sm:inline">Get Started</span>
          <span className="sm:hidden">Start</span>
          <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4" />
        </Link>
      </div>
    </nav>
  );
}
