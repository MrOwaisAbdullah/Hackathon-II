"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Check, ChevronDown, ChevronUp, ArrowRight } from "lucide-react";
import { useState } from "react";
import { MarketingHeader } from "@/components/layout/MarketingHeader";
import { MarketingFooter } from "@/components/layout/MarketingFooter";

const tiers = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for small teams getting started",
    features: [
      "Up to 5 users",
      "Basic task management",
      "3 active projects",
      "Kanban board view",
      "Email support",
      "7-day data retention"
    ],
    limitations: [
      "No AI assistant",
      "No time tracking",
      "No custom workflows"
    ],
    cta: "Get Started Free",
    highlighted: false,
    href: "/signup"
  },
  {
    name: "Pro",
    price: "$29",
    period: "per user/month",
    description: "For growing teams that need more power",
    features: [
      "Unlimited users",
      "Unlimited projects",
      "All views (Kanban, List, Calendar)",
      "AI task assistant",
      "Advanced workflows",
      "Time tracking",
      "Custom fields",
      "Priority support",
      "30-day data retention",
      "Advanced analytics"
    ],
    limitations: [],
    cta: "Start 14-Day Trial",
    highlighted: true,
    href: "/signup?plan=pro"
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "pricing",
    description: "For large organizations with advanced needs",
    features: [
      "Everything in Pro",
      "SSO / SAML authentication",
      "Unlimited data retention",
      "Dedicated account manager",
      "99.99% uptime SLA",
      "Custom integrations",
      "Audit logs",
      "Advanced security controls",
      "On-premise deployment option",
      "24/7 phone support"
    ],
    limitations: [],
    cta: "Contact Sales",
    highlighted: false,
    href: "/contact"
  }
];

const faqs = [
  {
    question: "Can I switch plans at any time?",
    answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we&#39;ll prorate your billing accordingly."
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards (Visa, MasterCard, American Express) and PayPal. For Enterprise plans, we also offer invoicing and wire transfers."
  },
  {
    question: "Is there a free trial for paid plans?",
    answer: "Yes! Pro plans come with a 14-day free trial. No credit card required to start. You'll only be charged after the trial period ends."
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Absolutely. You can cancel your subscription at any time. Your access will continue until the end of your billing period with no additional charges."
  },
  {
    question: "Do you offer discounts for nonprofits or education?",
    answer: "Yes, we offer special pricing for qualified nonprofits and educational institutions. Contact our sales team to learn more."
  }
];

const comparisonData = [
  { feature: "Users", free: "Up to 5", pro: "Unlimited", enterprise: "Unlimited" },
  { feature: "Projects", free: "3 active", pro: "Unlimited", enterprise: "Unlimited" },
  { feature: "Task Views", free: "Kanban", pro: "All views", enterprise: "All views" },
  { feature: "AI Assistant", free: false, pro: true, enterprise: true },
  { feature: "Time Tracking", free: false, pro: true, enterprise: true },
  { feature: "Custom Workflows", free: false, pro: true, enterprise: true },
  { feature: "Advanced Analytics", free: false, pro: true, enterprise: true },
  { feature: "SSO / SAML", free: false, pro: false, enterprise: true },
  { feature: "99.99% SLA", free: false, pro: false, enterprise: true },
  { feature: "Dedicated Account Manager", free: false, pro: false, enterprise: true },
  { feature: "Data Retention", free: "7 days", pro: "30 days", enterprise: "Unlimited" },
  { feature: "Support", free: "Email", pro: "Priority", enterprise: "24/7 Phone" }
];

export default function PricingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

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
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6">
              SIMPLE PRICING FOR <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-lime-300 to-emerald-400">
                TEAMS OF ALL SIZES.
              </span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Start free, upgrade when you&#39;re ready. No hidden fees, no surprises.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="relative py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {tiers.map((tier, index) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`relative rounded-3xl p-8 border ${
                  tier.highlighted
                    ? "bg-gradient-to-b from-lime-400/10 to-zinc-900 border-lime-500/50 shadow-2xl shadow-lime-400/10 scale-105"
                    : "bg-zinc-900/50 border-zinc-800"
                }`}
              >
                {tier.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-lime-400 text-black text-xs font-bold rounded-full uppercase tracking-wider">
                    Most Popular
                  </div>
                )}

                <div className="mb-8">
                  <h3 className="text-2xl font-black mb-2">{tier.name}</h3>
                  <p className="text-zinc-400 text-sm mb-6">{tier.description}</p>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-5xl font-black">{tier.price}</span>
                    {tier.period !== "forever" && (
                      <span className="text-zinc-400">/{tier.period}</span>
                    )}
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  {tier.features.map((feature, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-lime-400 shrink-0 mt-0.5" />
                      <span className="text-zinc-300">{feature}</span>
                    </div>
                  ))}
                  {tier.limitations.map((limitation, i) => (
                    <div key={i} className="flex items-start gap-3 opacity-50">
                      <div className="w-5 h-5 rounded-full border border-zinc-600 shrink-0 mt-0.5" />
                      <span className="text-zinc-500 line-through">{limitation}</span>
                    </div>
                  ))}
                </div>

                <Link
                  href={tier.href}
                  className={`block w-full py-4 rounded-xl text-center font-bold transition-all ${
                    tier.highlighted
                      ? "bg-lime-400 text-black hover:bg-lime-300 shadow-lg shadow-lime-400/20"
                      : "bg-zinc-800 text-white hover:bg-zinc-700"
                  }`}
                >
                  {tier.cta}
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="relative py-20 px-4 bg-zinc-900/50">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
              COMPARE FEATURES
            </h2>
            <p className="text-xl text-zinc-400">
              Side-by-side comparison of all plans
            </p>
          </motion.div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px]">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-4 px-4 font-bold text-zinc-400">Feature</th>
                  <th className="text-center py-4 px-4 font-bold">Free</th>
                  <th className="text-center py-4 px-4 font-bold text-lime-400">Pro</th>
                  <th className="text-center py-4 px-4 font-bold">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((row, index) => (
                  <tr key={index} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                    <td className="py-4 px-4 font-medium text-zinc-300">{row.feature}</td>
                    <td className="py-4 px-4 text-center text-zinc-400">
                      {typeof row.free === "boolean" ? (
                        row.free ? <Check className="w-5 h-5 text-lime-400 mx-auto" /> : "—"
                      ) : (
                        row.free
                      )}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {typeof row.pro === "boolean" ? (
                        row.pro ? <Check className="w-5 h-5 text-lime-400 mx-auto" /> : "—"
                      ) : (
                        <span className="text-lime-400 font-medium">{row.pro}</span>
                      )}
                    </td>
                    <td className="py-4 px-4 text-center text-zinc-400">
                      {typeof row.enterprise === "boolean" ? (
                        row.enterprise ? <Check className="w-5 h-5 text-lime-400 mx-auto" /> : "—"
                      ) : (
                        row.enterprise
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
              FREQUENTLY ASKED QUESTIONS
            </h2>
            <p className="text-xl text-zinc-400">
              Everything you need to know about pricing
            </p>
          </motion.div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="rounded-2xl bg-zinc-900/50 border border-zinc-800 overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full px-6 py-5 flex justify-between items-center text-left hover:bg-zinc-800/30 transition-colors"
                  aria-expanded={openFaq === index}
                >
                  <span className="font-bold text-lg pr-8">{faq.question}</span>
                  {openFaq === index ? (
                    <ChevronUp className="w-5 h-5 text-lime-400 shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-zinc-500 shrink-0" />
                  )}
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    openFaq === index ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
                  }`}
                >
                  <div className="px-6 pb-5 text-zinc-400 leading-relaxed">
                    {faq.answer}
                  </div>
                </div>
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
            <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-6">
              READY TO GET STARTED?
            </h2>
            <p className="text-xl text-zinc-400 mb-12">
              Start your free trial today. No credit card required.
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-10 py-5 bg-lime-400 text-black text-xl font-bold rounded-xl hover:bg-lime-300 transition-all shadow-lg shadow-lime-400/20"
            >
              Start Your Free Trial <ArrowRight className="w-6 h-6" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <MarketingFooter />
    </main>
  );
}
