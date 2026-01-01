"use client";

import { motion } from "framer-motion";
import { useState } from "react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: false,
    weeklyReport: true,
    theme: "light",
  });

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground mb-8">Manage your account settings</p>

        <div className="max-w-2xl space-y-6">
          {/* Profile Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-card rounded-lg border border-border p-6"
          >
            <h2 className="font-semibold text-lg mb-4">Profile</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Display Name</label>
                <input
                  type="text"
                  defaultValue="Admin User"
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  defaultValue="admin@test.com"
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background"
                />
              </div>
            </div>
          </motion.div>

          {/* Notifications Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card rounded-lg border border-border p-6"
          >
            <h2 className="font-semibold text-lg mb-4">Notifications</h2>
            <div className="space-y-4">
              {[
                { key: "notifications", label: "Push Notifications" },
                { key: "emailAlerts", label: "Email Alerts" },
                { key: "weeklyReport", label: "Weekly Summary Report" },
              ].map((setting) => (
                <div key={setting.key} className="flex items-center justify-between">
                  <span>{setting.label}</span>
                  <button
                    onClick={() => setSettings({ ...settings, [setting.key]: !settings[setting.key as keyof typeof settings] })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings[setting.key as keyof typeof settings] ? "bg-primary" : "bg-muted"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                        settings[setting.key as keyof typeof settings] ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Danger Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card rounded-lg border border-destructive/20 p-6"
          >
            <h2 className="font-semibold text-lg mb-4 text-destructive">Danger Zone</h2>
            <div className="flex gap-4">
              <button className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors">
                Export Data
              </button>
              <button className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:opacity-90 transition-opacity">
                Delete Account
              </button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
