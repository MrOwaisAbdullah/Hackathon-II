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
      <head>
        {/* Suppress ChatKit domain verification errors BEFORE loading ChatKit */}
        <Script id="chatkit-error-handler" strategy="beforeInteractive">
          {`
            window.addEventListener('unhandledrejection', function(event) {
              // Ignore ChatKit domain verification errors for self-hosted backend
              var reason = event.reason;
              if (reason && typeof reason === 'object') {
                var message = reason.message || String(reason);
                if (message.includes('Domain verification failed') ||
                    message.includes('domain_keys/verify')) {
                  console.log('[ChatKit] Suppressed domain verification error (self-hosted backend)');
                  event.preventDefault();
                }
              }
            });
          `}
        </Script>
      </head>
      <body className="antialiased">
        {/* ChatKit web component script - required for @openai/chatkit-react to work */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
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
