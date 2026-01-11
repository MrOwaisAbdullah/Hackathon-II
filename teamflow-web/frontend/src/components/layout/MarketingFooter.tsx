import Link from "next/link";
import { Github, Twitter, Linkedin } from "lucide-react";

/**
 * MarketingFooter - Consistent footer for all marketing/landing pages
 *
 * Used on: Home, Pricing, Privacy, Terms, Contact
 * NOT used on: Dashboard pages (which have their own layout)
 */
export function MarketingFooter() {
  const socialLinks = {
    github: "https://github.com/mrowaisabdullah",
    twitter: "https://twitter.com/mrowaisabdullah",
    linkedin: "https://linkedin.com/in/mrowaisabdullah",
  };

  return (
    <footer className="border-t border-zinc-800 py-16 bg-zinc-950">
      <div className="max-w-7xl mx-auto px-6">
        {/* Main Footer Content */}
        <div className="grid md:grid-cols-4 gap-12 mb-16">
          {/* Brand Column */}
          <div className="col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 rounded-lg bg-lime-400 flex items-center justify-center">
                <span className="text-black font-bold">T</span>
              </div>
              <span className="font-bold text-xl tracking-tight">TeamFlow</span>
            </Link>

            <p className="text-zinc-500 max-w-sm mb-6">
              The modern operating system for forward-thinking creative agencies.
              Built for speed, designed for clarity.
            </p>

            {/* Creator Credit */}
            <div className="text-sm text-zinc-600">
              <span className="text-zinc-500">Created by </span>
              <a
                href={socialLinks.github}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lime-400 hover:text-lime-300 transition-colors font-medium"
              >
                @mrowaisabdullah
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="font-bold text-white mb-6">Product</h4>
            <ul className="space-y-4 text-zinc-500">
              <li>
                <Link href="/#features" className="hover:text-lime-400 transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="hover:text-lime-400 transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-lime-400 transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="font-bold text-white mb-6">Company</h4>
            <ul className="space-y-4 text-zinc-500">
              <li>
                <Link href="/about" className="hover:text-lime-400 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-lime-400 transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Footer: Credits + Legal + Social */}
        <div className="pt-8 border-t border-zinc-900">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            {/* Left: Copyright + Creator */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 text-sm">
              <p className="text-zinc-600">
                © {new Date().getFullYear()} TeamFlow Inc. All rights reserved.
              </p>
              <span className="hidden sm:inline text-zinc-800">•</span>
              <p className="text-zinc-600">
                Built by{" "}
                <a
                  href={socialLinks.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-zinc-500 hover:text-lime-400 transition-colors font-medium"
                >
                  Owais Abdullah
                </a>
              </p>
            </div>

            {/* Center: Legal Links */}
            <div className="flex gap-6 text-sm">
              <Link
                href="/privacy"
                className="text-zinc-600 hover:text-white transition-colors"
              >
                Privacy
              </Link>
              <Link
                href="/terms"
                className="text-zinc-600 hover:text-white transition-colors"
              >
                Terms
              </Link>
            </div>

            {/* Right: Social Links */}
            <div className="flex gap-4">
              <a
                href={socialLinks.github}
                target="_blank"
                rel="noopener noreferrer"
                className="text-zinc-600 hover:text-lime-400 transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href={socialLinks.twitter}
                target="_blank"
                rel="noopener noreferrer"
                className="text-zinc-600 hover:text-lime-400 transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href={socialLinks.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="text-zinc-600 hover:text-lime-400 transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
