"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { MarketingHeader } from "@/components/layout/MarketingHeader";
import { MarketingFooter } from "@/components/layout/MarketingFooter";

export default function PrivacyPage() {
  const lastUpdated = "January 11, 2026";

  const sections = [
    {
      title: "1. Information We Collect",
      content: [
        {
          subtitle: "Personal Information",
          text: "We collect information you provide directly to us, including name, email address, company information, and any other information you choose to provide when creating an account, communicating with us, or using our services."
        },
        {
          subtitle: "Account Data",
          text: "We store data related to your TeamFlow account, including user profiles, project information, tasks, time entries, and any content you create or upload to the platform."
        },
        {
          subtitle: "Payment Information",
          text: "Payment processing is handled by third-party payment processors (such as Stripe). We do not store your complete credit card information on our servers."
        },
        {
          subtitle: "Usage Data",
          text: "We automatically collect information about your use of the Service, including IP address, browser type, device information, pages viewed, and timestamps."
        },
        {
          subtitle: "Cookies and Tracking",
          text: "We use cookies and similar technologies to collect information about your browsing activities, preferences, and device identifiers. You can manage cookie preferences through your browser settings."
        }
      ]
    },
    {
      title: "2. How We Use Your Information",
      content: [
        {
          subtitle: "Service Delivery",
          text: "To provide, maintain, and improve the Service, process transactions, send you technical notices and support messages, and respond to your comments, questions, and requests."
        },
        {
          subtitle: "Security and Fraud Prevention",
          text: "To verify your identity, prevent fraud, protect the security of our services, detect and prevent malicious activity, and enforce our Terms of Service."
        },
        {
          subtitle: "Analytics and Improvements",
          text: "To analyze usage patterns, improve our Service, develop new features, and conduct research on user behavior and preferences."
        },
        {
          subtitle: "Communications",
          text: "To send you transactional and promotional communications, updates about new features, product announcements, and other information we think may be of interest to you."
        }
      ]
    },
    {
      title: "3. Information Sharing",
      content: [
        {
          subtitle: "Service Providers",
          text: "We share information with third-party service providers who perform services on our behalf, such as hosting, data analysis, payment processing, and email delivery."
        },
        {
          subtitle: "Business Transfers",
          text: "In connection with any merger, sale of company assets, financing, or acquisition of all or a portion of our business, your information may be transferred."
        },
        {
          subtitle: "Legal Requirements",
          text: "We may disclose information if required to do so by law or in response to valid requests by public authorities, or to protect our rights, property, or safety."
        },
        {
          subtitle: "With Your Consent",
          text: "We may share your information with your consent or at your direction, such as when you authorize us to share data with third-party applications or services."
        }
      ]
    },
    {
      title: "4. Data Security and Retention",
      content: [
        {
          subtitle: "Security Measures",
          text: "We implement industry-standard security measures, including encryption, access controls, and regular security audits to protect your information from unauthorized access, alteration, or destruction."
        },
        {
          subtitle: "Data Retention",
          text: "We retain your information for as long as necessary to provide the Service and fulfill the purposes outlined in this policy. For paid plans, data is retained according to your subscription tier. You can request deletion of your account and associated data at any time."
        },
        {
          subtitle: "Data Backup",
          text: "We maintain secure backups of your data to prevent data loss. Backups are encrypted and stored in secure, geographically distributed data centers."
        }
      ]
    },
    {
      title: "5. Your Rights and Choices",
      content: [
        {
          subtitle: "Access and Portability",
          text: "You have the right to request access to the personal information we hold about you and receive a copy in a structured, machine-readable format."
        },
        {
          subtitle: "Correction and Deletion",
          text: "You may request correction of inaccurate information or deletion of your personal information, subject to certain legal and operational requirements."
        },
        {
          subtitle: "Opt-Out of Marketing",
          text: "You may opt out of receiving promotional communications from us by following the unsubscribe instructions in those emails or by contacting us directly."
        },
        {
          subtitle: "Data Processing Restriction",
          text: "In certain jurisdictions, you have the right to restrict or object to the processing of your personal information."
        },
        {
          subtitle: "Account Closure",
          text: "You may close your TeamFlow account at any time by contacting us or using the account deletion feature in your settings. This will result in the deletion of your account and associated data."
        }
      ]
    },
    {
      title: "6. Third-Party Links and Integrations",
      content: [
        {
          subtitle: "External Links",
          text: "The Service may contain links to third-party websites or services. We are not responsible for the privacy practices of these third parties. We encourage you to review the privacy policies of any third-party sites you visit."
        },
        {
          subtitle: "Integrations",
          text: "TeamFlow integrates with various third-party services. When you authorize an integration, certain data may be shared with that service according to their privacy policy. You can revoke integrations at any time through your account settings."
        }
      ]
    },
    {
      title: "7. Children's Privacy",
      content: [
        {
          subtitle: "Age Requirement",
          text: "The Service is intended for users who are at least 16 years old. We do not knowingly collect personal information from children under 16. If we become aware that we have collected such information, we will take steps to delete it."
        }
      ]
    },
    {
      title: "8. International Data Transfers",
      content: [
        {
          subtitle: "Global Service",
          text: "Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy."
        },
        {
          subtitle: "EU Data Protection",
          text: "For users in the European Economic Area, we rely on Standard Contractual Clauses and other legal mechanisms to ensure adequate protection of personal data transferred outside the EEA."
        }
      ]
    },
    {
      title: "9. Updates to This Policy",
      content: [
        {
          subtitle: "Policy Changes",
          text: "We may update this Privacy Policy from time to time. We will notify you of material changes by posting the new policy on the Service and updating the 'Last Updated' date. Continued use of the Service after changes constitutes acceptance of the updated policy."
        }
      ]
    },
    {
      title: "10. Contact Us",
      content: [
        {
          subtitle: "Questions and Concerns",
          text: "If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us at:"
        },
        {
          subtitle: "Contact Information",
          text: "Email: privacy@teamflow.com\nAddress: TeamFlow Inc., 123 Innovation Drive, San Francisco, CA 94105, USA"
        }
      ]
    }
  ];

  return (
    <main className="min-h-screen bg-zinc-950 text-white selection:bg-lime-400 selection:text-black font-sans">
      {/* Background Effects */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-lime-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none" />

      {/* Header */}
      <MarketingHeader />

      {/* Header Section */}
      <section className="relative pt-32 pb-16 px-4">
        <div className="max-w-4xl mx-auto">
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
            <h1 className="text-5xl md:text-6xl font-black tracking-tighter mb-6">
              PRIVACY POLICY
            </h1>
            <p className="text-zinc-400 text-lg">
              Last Updated: {lastUpdated}
            </p>
          </motion.div>
        </div>
      </section>

      {/* Content Section */}
      <section className="relative py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="prose prose-invert max-w-none"
          >
            <div className="text-zinc-300 text-lg leading-relaxed mb-12">
              <p>
                At TeamFlow, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our task management and collaboration platform. Please read this policy carefully.
              </p>
            </div>

            {sections.map((section, sectionIndex) => (
              <motion.div
                key={sectionIndex}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.5, delay: sectionIndex * 0.05 }}
                className="mb-16"
              >
                <h2 className="text-2xl md:text-3xl font-black text-white mb-8 tracking-tight">
                  {section.title}
                </h2>

                {section.content.map((item, itemIndex) => (
                  <div key={itemIndex} className="mb-8 last:mb-0">
                    <h3 className="text-xl font-bold text-lime-400 mb-3">
                      {item.subtitle}
                    </h3>
                    <p className="text-zinc-300 leading-relaxed whitespace-pre-line">
                      {item.text}
                    </p>
                  </div>
                ))}
              </motion.div>
            ))}

            {/* Closing Statement */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="mt-16 p-8 rounded-2xl bg-zinc-900/50 border border-zinc-800"
            >
              <p className="text-zinc-300 leading-relaxed text-lg">
                By using TeamFlow, you acknowledge that you have read, understood, and agree to be bound by this Privacy Policy. If you do not agree with this policy, please do not use our Service.
              </p>
            </motion.div>
          </motion.div>
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
            <h2 className="text-3xl md:text-4xl font-black tracking-tighter mb-6">
              HAVE QUESTIONS?
            </h2>
            <p className="text-xl text-zinc-400 mb-8">
              We&#39;re here to help. Contact us anytime.
            </p>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-8 py-4 bg-lime-400 text-black text-lg font-bold rounded-xl hover:bg-lime-300 transition-all shadow-lg shadow-lime-400/20"
            >
              Contact Us
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <MarketingFooter />
    </main>
  );
}
