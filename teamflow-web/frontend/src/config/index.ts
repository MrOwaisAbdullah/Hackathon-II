/** Application configuration. */

export const config = {
  /** Backend API base URL */
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  /** Polling interval for real-time updates (ms) */
  pollingInterval: 10000,

  /** Enable debug logging */
  debug: process.env.NODE_ENV === "development",

  /** App version */
  version: "0.1.0",
} as const;

export type Config = typeof config;
