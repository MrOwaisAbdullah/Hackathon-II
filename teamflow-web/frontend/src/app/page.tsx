"use client";

import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { CheckCircle2, Zap, Shield, BarChart3, ArrowRight } from "lucide-react";
import { MarketingHeader } from "@/components/layout/MarketingHeader";
import { MarketingFooter } from "@/components/layout/MarketingFooter";

export default function HomePage() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <main className="flex flex-col min-h-screen bg-zinc-950 text-white selection:bg-lime-400 selection:text-black font-sans">
      
      {/* Background Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-lime-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none" />

      {/* Header */}
      <MarketingHeader />

      {/* Hero Section */}
      <section ref={containerRef} className="relative min-h-screen flex flex-col items-center justify-center pt-32 pb-20 px-4 overflow-hidden">
        <motion.div
          style={{ y, opacity }}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="z-10 max-w-5xl w-full text-center"
        >
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-zinc-800 bg-zinc-900/50 backdrop-blur-md shadow-sm mb-8"
          >
            <div className="w-2 h-2 rounded-full bg-lime-400 animate-ping" />
            <span className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Intelligent Task Management</span>
          </motion.div>

          <h1 className="text-6xl md:text-9xl font-black tracking-tighter mb-8 leading-[0.85] text-white">
            SIMPLIFY YOUR <br />
            <span className="relative inline-block text-transparent bg-clip-text bg-gradient-to-r from-lime-300 to-emerald-400">
              WORKFLOW.
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-zinc-400 mb-12 max-w-2xl mx-auto leading-relaxed">
            TeamFlow helps you <strong className="text-white">think less</strong>, plan smarter, and execute faster. 
            The agency operating system for high-performance teams.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 justify-center items-center">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="/signup"
                className="px-8 py-4 bg-lime-400 text-black rounded-xl hover:bg-lime-300 transition-all font-bold text-lg shadow-xl shadow-lime-400/20 flex items-center gap-2"
              >
                Start Free Trial <ArrowRight className="w-5 h-5" />
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="/login"
                className="px-8 py-4 bg-zinc-900 text-white border border-zinc-800 rounded-xl hover:border-zinc-700 hover:bg-zinc-800 transition-all font-bold text-lg"
              >
                Live Demo
              </Link>
            </motion.div>
          </div>

          <div className="mt-20 pt-10 border-t border-zinc-800/50 flex flex-wrap justify-center gap-8 md:gap-16 opacity-70">
            {["Spotify", "Netflix", "Linear", "Vercel", "Airbnb"].map((brand) => (
              <span key={brand} className="text-xl font-bold text-zinc-600 uppercase tracking-widest">{brand}</span>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 relative z-10 bg-zinc-950">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-24">
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-6">BUILT FOR VELOCITY.</h2>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">Everything you need to manage complex projects without the complexity.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: "Lightning Fast",
                desc: "Optimized for speed. Keyboard shortcuts, instant transitions, and zero lag."
              },
              {
                icon: Shield,
                title: "Enterprise Secure",
                desc: "Bank-grade security with role-based access control and audit logs."
              },
              {
                icon: BarChart3,
                title: "Real-time Analytics",
                desc: "Live dashboards giving you instant insights into team performance."
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -10 }}
                className="p-8 rounded-3xl bg-zinc-900/50 border border-zinc-800 hover:border-lime-500/30 transition-all"
              >
                <div className="w-14 h-14 rounded-2xl bg-zinc-800 flex items-center justify-center mb-6">
                  <feature.icon className="w-7 h-7 text-lime-400" />
                </div>
                <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                <p className="text-zinc-400 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Preview Section */}
      <section className="py-20 bg-zinc-900 border-y border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-4xl font-black tracking-tighter mb-6">MASTER YOUR <br /><span className="text-lime-400">CHAOS.</span></h2>
            <div className="space-y-6">
              {[
                "Drag-and-drop Kanban boards",
                "Automated workflow triggers",
                "Integrated time tracking",
                "Client portal access"
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4">
                  <CheckCircle2 className="w-6 h-6 text-lime-400 shrink-0" />
                  <span className="text-xl font-medium text-zinc-300">{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="relative">
            <div className="absolute inset-0 bg-lime-500/20 blur-[100px] rounded-full pointer-events-none" />
            <div className="relative bg-black border border-zinc-800 rounded-2xl p-6 shadow-2xl rotate-3 hover:rotate-0 transition-transform duration-500">
              {/* Mock UI */}
              <div className="flex gap-4 mb-6">
                <div className="w-1/3 h-32 bg-zinc-900 rounded-xl animate-pulse" />
                <div className="w-1/3 h-32 bg-zinc-900 rounded-xl animate-pulse delay-75" />
                <div className="w-1/3 h-32 bg-zinc-900 rounded-xl animate-pulse delay-150" />
              </div>
              <div className="space-y-3">
                <div className="h-4 w-3/4 bg-zinc-800 rounded" />
                <div className="h-4 w-1/2 bg-zinc-800 rounded" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-lime-400/5" />
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <h2 className="text-5xl md:text-7xl font-black tracking-tighter mb-8">READY TO SHIP?</h2>
          <p className="text-xl text-zinc-400 mb-12">Join 10,000+ teams building the future with TeamFlow.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="px-10 py-5 bg-lime-400 text-black text-xl font-bold rounded-xl hover:bg-lime-300 transition-colors shadow-lg shadow-lime-400/20">
              Start Your Free Trial
            </Link>
            <Link href="/login" className="px-10 py-5 bg-zinc-900 text-white text-xl font-bold rounded-xl border border-zinc-800 hover:bg-zinc-800 transition-colors">
              Talk to Sales
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <MarketingFooter />
    </main>
  );
}