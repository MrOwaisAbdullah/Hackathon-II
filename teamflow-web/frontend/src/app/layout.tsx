import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { Providers } from "@/components/providers/Providers";
import { Toaster } from "sonner";
import { ChatWidget } from "@/components/chat";

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
        <Providers>
          <ThemeProvider>
            <AuthProvider>
              {children}
              {/* ChatWidget - Positioned via fixed positioning */}
              <ChatWidget
                apiUrl={process.env.NEXT_PUBLIC_API_URL}
                position="bottom-right"
              />
            </AuthProvider>
          </ThemeProvider>
        </Providers>
        <Toaster position="top-right" richColors closeButton />
      </body>
    </html>
  );
}
