"use client";

/** Authentication hook using Better Auth for session management.
 *
 * Integrates with our FastAPI backend for JWT authentication.
 */

import { useEffect, useState } from "react";
import React from "react";

import type { User } from "@/types";
import { api } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      // Skip SSR
      if (typeof window === "undefined") return;

      try {
        const token = localStorage.getItem("auth_token");
        if (token) {
          // Call the /me endpoint to get current user
          const response = await api.get<{ user: User }>("/api/v1/auth/me");
          setUser(response.data.user);
        }
      } catch (error) {
        console.error("Session check failed:", error);
        // Clear invalid token
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
        }
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post<{
      user: User;
      access_token: string;
    }>("/api/v1/auth/login", {
      email,
      password,
    });

    const { user: loggedInUser, access_token } = response.data;
    localStorage.setItem("auth_token", access_token);
    setUser(loggedInUser);
  };

  const logout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
    setUser(null);
  };

  const refreshUser = async () => {
    const response = await api.get<{ user: User }>("/api/v1/auth/me");
    setUser(response.data.user);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
