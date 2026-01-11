"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, FormEvent } from "react";
import { Mail, MessageSquare, Github, Twitter, Linkedin, Send, ArrowRight, CheckCircle2 } from "lucide-react";
import { MarketingHeader } from "@/components/layout/MarketingHeader";
import { MarketingFooter } from "@/components/layout/MarketingFooter";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1500));

    setIsSubmitting(false);
    setIsSubmitted(true);

    // Reset form after 3 seconds
    setTimeout(() => {
      setIsSubmitted(false);
      setFormData({ name: "", email: "", subject: "", message: "" });
    }, 3000);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const contactInfo = [
    {
      icon: Mail,
      title: "Support",
      email: "support@teamflow.com",
      description: "Get help with technical issues, bugs, or feature requests."
    },
    {
      icon: MessageSquare,
      title: "Sales",
      email: "sales@teamflow.com",
      description: "Interested in TeamFlow for your team? Let's talk."
    }
  ];

  const socialLinks = [
    {
      name: "GitHub",
      icon: Github,
      href: "https://github.com/teamflow",
      description: "Check out our open-source projects"
    },
    {
      name: "Twitter",
      icon: Twitter,
      href: "https://twitter.com/teamflow",
      description: "Follow for updates and tips"
    },
    {
      name: "LinkedIn",
      icon: Linkedin,
      href: "https://linkedin.com/company/teamflow",
      description: "Connect with our team"
    }
  ];

  return (
    <main className="min-h-screen bg-zinc-950 text-white selection:bg-lime-400 selection:text-black font-sans">
      {/* Background Effects */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-lime-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none" />

      {/* Header */}
      <MarketingHeader />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link
              href="/"
              className="inline-flex items-center text-lime-400 hover:text-lime-300 transition-colors mb-8 text-sm font-medium"
            >
              ← Back to Home
            </Link>
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6">
              GET IN <span className="text-transparent bg-clip-text bg-gradient-to-r from-lime-300 to-emerald-400">TOUCH.</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Form Section */}
      <section className="relative py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-5 gap-12">
            {/* Contact Info */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="lg:col-span-2 space-y-8"
            >
              <div>
                <h2 className="text-2xl font-black tracking-tighter mb-6">CONTACT INFO</h2>
                <p className="text-zinc-400 leading-relaxed">
                  Choose the right channel for your inquiry. We typically respond within 24 hours.
                </p>
              </div>

              {contactInfo.map((info, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                  className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800 hover:border-lime-500/30 transition-all group"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-zinc-800 flex items-center justify-center group-hover:bg-lime-400 transition-colors">
                      <info.icon className="w-6 h-6 text-lime-400 group-hover:text-black transition-colors" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-lg mb-1">{info.title}</h3>
                      <a
                        href={`mailto:${info.email}`}
                        className="text-lime-400 hover:text-lime-300 transition-colors text-sm"
                      >
                        {info.email}
                      </a>
                      <p className="text-zinc-500 text-sm mt-2">{info.description}</p>
                    </div>
                  </div>
                </motion.div>
              ))}

              {/* Social Links */}
              <div className="pt-8 border-t border-zinc-800">
                <h3 className="font-bold text-lg mb-4">FOLLOW US</h3>
                <div className="flex gap-4">
                  {socialLinks.map((social, index) => (
                    <motion.a
                      key={index}
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                      whileHover={{ y: -5 }}
                      className="w-12 h-12 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center hover:bg-lime-400 hover:border-lime-400 transition-all group"
                      aria-label={social.name}
                    >
                      <social.icon className="w-5 h-5 text-zinc-400 group-hover:text-black transition-colors" />
                    </motion.a>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="lg:col-span-3"
            >
              <div className="p-8 rounded-3xl bg-zinc-900/50 border border-zinc-800">
                <h2 className="text-2xl font-black tracking-tighter mb-6">SEND A MESSAGE</h2>

                {isSubmitted ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="py-12 text-center"
                  >
                    <CheckCircle2 className="w-16 h-16 text-lime-400 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold mb-2">Message Sent!</h3>
                    <p className="text-zinc-400">We'll get back to you within 24 hours.</p>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-zinc-400 mb-2">
                          Name *
                        </label>
                        <input
                          type="text"
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          required
                          className="w-full px-4 py-3 rounded-xl bg-zinc-800 border border-zinc-700 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-lime-400 focus:border-transparent transition-all"
                          placeholder="John Doe"
                        />
                      </div>
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-zinc-400 mb-2">
                          Email *
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          required
                          className="w-full px-4 py-3 rounded-xl bg-zinc-800 border border-zinc-700 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-lime-400 focus:border-transparent transition-all"
                          placeholder="john@company.com"
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-zinc-400 mb-2">
                        Subject *
                      </label>
                      <input
                        type="text"
                        id="subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 rounded-xl bg-zinc-800 border border-zinc-700 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-lime-400 focus:border-transparent transition-all"
                        placeholder="How can we help?"
                      />
                    </div>

                    <div>
                      <label htmlFor="message" className="block text-sm font-medium text-zinc-400 mb-2">
                        Message *
                      </label>
                      <textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        required
                        rows={6}
                        className="w-full px-4 py-3 rounded-xl bg-zinc-800 border border-zinc-700 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-lime-400 focus:border-transparent transition-all resize-none"
                        placeholder="Tell us more about your inquiry..."
                      />
                    </div>

                    <motion.button
                      type="submit"
                      disabled={isSubmitting}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full py-4 bg-lime-400 text-black rounded-xl hover:bg-lime-300 transition-all font-bold text-lg flex items-center justify-center gap-2 shadow-lg shadow-lime-400/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          Send Message <Send className="w-5 h-5" />
                        </>
                      )}
                    </motion.button>
                  </form>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-20 px-4 bg-zinc-900/50">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-black tracking-tighter mb-4">
              COMMON QUESTIONS
            </h2>
            <p className="text-xl text-zinc-400">
              Quick answers to frequently asked questions
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                question: "What's your response time?",
                answer: "We typically respond to all inquiries within 24 hours on business days."
              },
              {
                question: "Do you offer phone support?",
                answer: "Phone support is available for Enterprise customers. Pro users receive email support."
              },
              {
                question: "Can I schedule a demo?",
                answer: "Yes! Contact our sales team at sales@teamflow.com to schedule a personalized demo."
              },
              {
                question: "Where are you located?",
                answer: "We're based in San Francisco, CA with team members across the globe."
              }
            ].map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800"
              >
                <h3 className="font-bold text-lg mb-2">{faq.question}</h3>
                <p className="text-zinc-400">{faq.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-lime-400/5" />
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-6">
              READY TO GET STARTED?
            </h2>
            <p className="text-xl text-zinc-400 mb-12">
              Join thousands of teams already using TeamFlow
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="inline-flex items-center justify-center gap-2 px-10 py-5 bg-lime-400 text-black text-xl font-bold rounded-xl hover:bg-lime-300 transition-all shadow-lg shadow-lime-400/20"
              >
                Start Free Trial <ArrowRight className="w-6 h-6" />
              </Link>
              <Link
                href="/pricing"
                className="inline-flex items-center justify-center px-10 py-5 bg-zinc-900 text-white text-xl font-bold rounded-xl border border-zinc-800 hover:bg-zinc-800 transition-all"
              >
                View Pricing
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <MarketingFooter />
    </main>
  );
}
