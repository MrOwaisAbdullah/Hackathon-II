import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: false,
  },
  output: 'standalone',
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  // Cache busting for deployments
  generateBuildId: () => {
    // Use current timestamp for cache busting
    return `build-${Date.now()}`;
  },
  // Disable static asset caching for development
  productionBrowserSourceMaps: false,
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
    return [
      {
        source: "/v1/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ];
  },
  // Add environment variable validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "",
  },
};

export default nextConfig;
