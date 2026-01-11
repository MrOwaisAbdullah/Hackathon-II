import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { Providers } from "@/components/providers/Providers";
import { Toaster } from "sonner";
import { ChatWidgetWrapper } from "@/components/chat/ChatWidgetWrapper";

export const metadata: Metadata = {
  title: "TeamFlow - Agency Task Management",
  description: "Task management CRM for creative agencies",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        {/* ChatKit web component script - required for @openai/chatkit-react to work */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
        {/* Suppress ChatKit domain verification errors for self-hosted backend */}
        <Script id="chatkit-error-handler" strategy="afterInteractive">
          {`
            if (typeof window !== 'undefined') {
              window.addEventListener('unhandledrejection', (event) => {
                // Ignore ChatKit domain verification errors
                if (event.reason?.message?.includes('Domain verification failed') ||
                    event.reason?.message?.includes('domain_keys/verify') ||
                    String(event.reason).includes('Domain verification failed')) {
                  console.log('[ChatKit] Suppressed domain verification error (self-hosted backend)');
                  event.preventDefault();
                }
              });
            }
          `}
        </Script>
        <Providers>
          <ThemeProvider>
            <AuthProvider>
              {children}
              {/* ChatWidget - Positioned via fixed positioning, hidden on /chat page */}
              <ChatWidgetWrapper />
            </AuthProvider>
          </ThemeProvider>
        </Providers>
        <Toaster position="top-right" richColors closeButton />
      </body>
    </html>
  );
}
