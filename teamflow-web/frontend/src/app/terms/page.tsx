"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { MarketingHeader } from "@/components/layout/MarketingHeader";
import { MarketingFooter } from "@/components/layout/MarketingFooter";

export default function TermsPage() {
  const lastUpdated = "January 11, 2026";

  const sections = [
    {
      title: "1. Acceptance of Terms",
      content: [
        {
          subtitle: "Agreement to Terms",
          text: "By accessing or using TeamFlow ('Service'), you agree to be bound by these Terms of Service ('Terms'). If you do not agree to these Terms, please do not use our Service. These Terms constitute a legally binding agreement between you and TeamFlow Inc."
        },
        {
          subtitle: "Age Requirement",
          text: "You must be at least 16 years old to use this Service. By using this Service, you represent that you are at least 16 years old and have the legal capacity to enter into these Terms."
        },
        {
          subtitle: "Changes to Terms",
          text: "We reserve the right to modify these Terms at any time. We will notify users of material changes by posting the updated Terms on the Service and updating the 'Last Updated' date. Your continued use of the Service after such changes constitutes acceptance of the new Terms."
        }
      ]
    },
    {
      title: "2. Account Responsibilities",
      content: [
        {
          subtitle: "Account Creation",
          text: "You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account or any other breach of security."
        },
        {
          subtitle: "Accurate Information",
          text: "You agree to provide accurate, current, and complete information during account registration and to update such information to keep it accurate, current, and complete. You must not use misleading or false information."
        },
        {
          subtitle: "Account Security",
          text: "You are responsible for maintaining the security of your account. You must not disclose your password to any third party or allow any third party to access your account. You are responsible for any activities conducted through your account, whether or not you authorized those activities."
        },
        {
          subtitle: "Account Termination",
          text: "We reserve the right to suspend or terminate your account at any time for any reason, including but not limited to violation of these Terms, fraudulent activity, or extended periods of inactivity."
        }
      ]
    },
    {
      title: "3. Service Terms",
      content: [
        {
          subtitle: "Service Description",
          text: "TeamFlow provides a task management and collaboration platform designed to help teams organize work, track progress, and communicate effectively. The Service includes features such as task management, project tracking, time tracking, team communication, and integrations with third-party services."
        },
        {
          subtitle: "Service Availability",
          text: "We strive to provide reliable service but do not guarantee uninterrupted or error-free operation. The Service may be temporarily unavailable for maintenance, updates, or other reasons. We are not liable for any loss or damage resulting from service interruptions."
        },
        {
          subtitle: "Service Modifications",
          text: "We reserve the right to modify, suspend, or discontinue any aspect of the Service at any time, including features, content, or functionality. We are not liable to you or any third party for any modification, suspension, or discontinuation of the Service."
        },
        {
          subtitle: "Third-Party Services",
          text: "The Service may integrate with or link to third-party services and applications. Your use of these third-party services is governed by their respective terms and conditions. We are not responsible for the practices or policies of third-party services."
        }
      ]
    },
    {
      title: "4. User Conduct and Content",
      content: [
        {
          subtitle: "Acceptable Use",
          text: "You agree to use the Service only for lawful purposes and in accordance with these Terms. You must not use the Service to: (a) harass, abuse, or harm others; (b) transmit viruses, malware, or malicious code; (c) interfere with or disrupt the Service; (d) attempt to gain unauthorized access; (e) violate any applicable laws or regulations."
        },
        {
          subtitle: "User Content",
          text: "You retain ownership of all content you submit to the Service. By submitting content, you grant us a license to use, modify, display, and distribute your content solely for the purpose of providing the Service. You represent that you have the right to grant this license."
        },
        {
          subtitle: "Content Responsibility",
          text: "You are solely responsible for all content you create, upload, or share through the Service. We do not pre-screen content but reserve the right to remove any content that violates these Terms or is otherwise objectionable."
        },
        {
          subtitle: "Prohibited Content",
          text: "You must not submit content that is illegal, defamatory, obscene, hateful, or that infringes on the rights of others. This includes content that violates intellectual property rights, privacy rights, or any other applicable law."
        }
      ]
    },
    {
      title: "5. Payment Terms",
      content: [
        {
          subtitle: "Subscription Plans",
          text: "TeamFlow offers various subscription plans with different features and pricing. Plan details are available on our website. Pricing is subject to change, but changes will not affect existing subscriptions until renewal."
        },
        {
          subtitle: "Billing and Renewal",
          text: "Paid subscriptions are billed in advance on a recurring basis (monthly or annually). Subscriptions automatically renew unless cancelled before the renewal date. You may cancel at any time through your account settings."
        },
        {
          subtitle: "Refund Policy",
          text: "We offer a 14-day free trial for paid plans. If you cancel before the trial ends, you will not be charged. Refunds for paid subscriptions are handled on a case-by-case basis. Contact our support team for refund requests."
        },
        {
          subtitle: "Payment Methods",
          text: "We accept major credit cards and other payment methods as displayed on our website. By providing payment information, you authorize us to charge your chosen payment method for the selected plan."
        }
      ]
    },
    {
      title: "6. Intellectual Property",
      content: [
        {
          subtitle: "TeamFlow Property",
          text: "The Service, including all content, features, and functionality, is owned by TeamFlow Inc. and is protected by copyright, trademark, and other intellectual property laws. You may not reproduce, distribute, or create derivative works without our express written permission."
        },
        {
          subtitle: "Trademarks",
          text: "TeamFlow, the TeamFlow logo, and other related names, logos, and designs are trademarks of TeamFlow Inc. You may not use our trademarks without prior written consent."
        },
        {
          subtitle: "User License",
          text: "We grant you a limited, non-exclusive, non-transferable license to use the Service for your personal or business purposes in accordance with these Terms. This license is revocable at any time."
        }
      ]
    },
    {
      title: "7. Privacy and Data",
      content: [
        {
          subtitle: "Privacy Policy",
          text: "Your use of the Service is also governed by our Privacy Policy, which describes how we collect, use, and protect your information. By using the Service, you consent to our data practices as described in the Privacy Policy."
        },
        {
          subtitle: "Data Ownership",
          text: "You retain ownership of all data you input into the Service. We will not sell, rent, or license your data to third parties except as described in our Privacy Policy or as required by law."
        },
        {
          subtitle: "Data Backup",
          text: "While we maintain backups and implement robust security measures, we cannot guarantee 100% data protection. You are responsible for maintaining your own backups of critical data."
        }
      ]
    },
    {
      title: "8. Disclaimers and Warranties",
      content: [
        {
          subtitle: "Service Provided 'As Is'",
          text: "THE SERVICE IS PROVIDED 'AS IS' AND 'AS AVAILABLE' WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT."
        },
        {
          subtitle: "No Guarantee of Results",
          text: "We do not guarantee that the Service will meet your requirements or that the Service will be uninterrupted, timely, secure, or error-free. We are not responsible for any loss of data or business disruptions."
        },
        {
          subtitle: "Third-Party Content",
          text: "The Service may contain links to or content from third parties. We do not endorse, warrant, or assume responsibility for any third-party content, products, or services."
        }
      ]
    },
    {
      title: "9. Limitation of Liability",
      content: [
        {
          subtitle: "Damages Exclusion",
          text: "TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, TEAMFLOW SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, OR BUSINESS INTERRUPTION, ARISING FROM OR RELATING TO THESE TERMS OR THE SERVICE."
        },
        {
          subtitle: "Liability Cap",
          text: "IN NO EVENT SHALL TEAMFLOW'S TOTAL LIABILITY TO YOU FOR ALL CLAIMS EXCEED THE AMOUNT YOU PAID FOR THE SERVICE IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM. SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF CERTAIN WARRANTIES OR LIMITATION OF LIABILITY, SO THE ABOVE LIMITATIONS MAY NOT APPLY TO YOU."
        }
      ]
    },
    {
      title: "10. Indemnification",
      content: [
        {
          subtitle: "User Indemnification",
          text: "You agree to indemnify, defend, and hold harmless TeamFlow and its officers, directors, employees, and agents from any claims, damages, losses, liabilities, and expenses (including legal fees) arising from: (a) your use of the Service; (b) your violation of these Terms; (c) your violation of any third-party rights; or (d) content you submit to the Service."
        }
      ]
    },
    {
      title: "11. Termination",
      content: [
        {
          subtitle: "Termination by User",
          text: "You may terminate your account at any time by contacting us or using the account deletion feature in your settings. Upon termination, your right to use the Service will immediately cease."
        },
        {
          subtitle: "Termination by TeamFlow",
          text: "We may suspend or terminate your account and access to the Service at our sole discretion, without prior notice, for any reason, including but not limited to violation of these Terms, fraudulent activity, or extended inactivity."
        },
        {
          subtitle: "Effect of Termination",
          text: "Upon termination, all rights and licenses granted to you in these Terms will immediately cease. We reserve the right to delete your account and all associated data, though we may retain certain information as required by law or for legitimate business purposes."
        }
      ]
    },
    {
      title: "12. Dispute Resolution",
      content: [
        {
          subtitle: "Governing Law",
          text: "These Terms are governed by and construed in accordance with the laws of the State of California, United States, without regard to its conflict of law principles."
        },
        {
          subtitle: "Arbitration Agreement",
          text: "Any dispute arising from or relating to these Terms or the Service shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association, except where prohibited by law."
        },
        {
          subtitle: "Class Action Waiver",
          text: "YOU AGREE TO RESOLVE DISPUTES ON AN INDIVIDUAL BASIS AND WAIVE ANY RIGHT TO PARTICIPATE IN A CLASS ACTION, CLASS ARBITRATION, OR OTHER REPRESENTATIVE PROCEEDING."
        }
      ]
    },
    {
      title: "13. General Provisions",
      content: [
        {
          subtitle: "Entire Agreement",
          text: "These Terms, together with our Privacy Policy and any other legal notices published on the Service, constitute the entire agreement between you and TeamFlow regarding the Service."
        },
        {
          subtitle: "Severability",
          text: "If any provision of these Terms is found to be unenforceable or invalid, that provision will be limited or eliminated to the minimum extent necessary so that the remaining Terms will remain in full force and effect."
        },
        {
          subtitle: "Waiver",
          text: "Our failure to enforce any right or provision of these Terms will not be considered a waiver of those rights. Any waiver of any provision of these Terms will be effective only if in writing and signed by us."
        },
        {
          subtitle: "Assignment",
          text: "You may not assign or transfer these Terms or your rights under these Terms without our prior written consent. We may freely assign these Terms without restriction."
        }
      ]
    },
    {
      title: "14. Contact Information",
      content: [
        {
          subtitle: "Questions and Communications",
          text: "If you have any questions about these Terms or need to contact us for any reason, please reach out to us at:"
        },
        {
          subtitle: "Contact Details",
          text: "Email: legal@teamflow.com\nAddress: TeamFlow Inc., 123 Innovation Drive, San Francisco, CA 94105, USA"
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
              TERMS OF SERVICE
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
                Welcome to TeamFlow. These Terms of Service govern your use of our task management and collaboration platform. By accessing or using TeamFlow, you agree to be bound by these Terms. Please read them carefully.
              </p>
            </div>

            {sections.map((section, sectionIndex) => (
              <motion.div
                key={sectionIndex}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.5, delay: sectionIndex * 0.03 }}
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
                By using TeamFlow, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service. If you do not agree with these Terms, please do not use our Service.
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
              READY TO GET STARTED?
            </h2>
            <p className="text-xl text-zinc-400 mb-8">
              Join thousands of teams using TeamFlow to work smarter.
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-8 py-4 bg-lime-400 text-black text-lg font-bold rounded-xl hover:bg-lime-300 transition-all shadow-lg shadow-lime-400/20"
            >
              Start Free Trial
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <MarketingFooter />
    </main>
  );
}
