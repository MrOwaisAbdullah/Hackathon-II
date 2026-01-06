"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useDeleteMyAccount } from "@/lib/query";
import { Download, Trash2, Loader2, AlertTriangle, Upload, Camera } from "lucide-react";
import { toast } from "sonner";

export default function SettingsPage() {
  const router = useRouter();
  const deleteMyAccount = useDeleteMyAccount();

  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: false,
    weeklyReport: true,
    theme: "light",
  });
  const [isDeleting, setIsDeleting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Profile state
  const [userName, setUserName] = useState("Admin User");
  const [userEmail, setUserEmail] = useState("admin@test.com");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // Load settings and profile from localStorage on mount
  useEffect(() => {
    const storedSettings = localStorage.getItem("notificationSettings");
    if (storedSettings) {
      setSettings(JSON.parse(storedSettings));
    }

    const storedAvatar = localStorage.getItem("userAvatar");
    if (storedAvatar) {
      setAvatarUrl(storedAvatar);
    }

    const storedName = localStorage.getItem("userName");
    if (storedName) {
      setUserName(storedName);
    }

    const storedEmail = localStorage.getItem("userEmail");
    if (storedEmail) {
      setUserEmail(storedEmail);
    }
  }, []);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("notificationSettings", JSON.stringify(settings));
  }, [settings]);

  // Handle notification toggle with toast feedback
  const handleNotificationToggle = (key: string) => {
    const newValue = !settings[key as keyof typeof settings];
    setSettings({ ...settings, [key]: newValue });

    // Show toast notification
    const settingLabels: Record<string, string> = {
      notifications: "Push notifications",
      emailAlerts: "Email alerts",
      weeklyReport: "Weekly summary report",
    };

    toast.success(
      `${settingLabels[key]} ${newValue ? 'enabled' : 'disabled'}`,
      { duration: 2000 }
    );
  };

  // Handle avatar upload
  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please select an image file");
      return;
    }

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast.error("Image must be less than 2MB");
      return;
    }

    // Create a preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      setAvatarUrl(base64String);
      localStorage.setItem("userAvatar", base64String);
      toast.success("Avatar updated successfully");
    };
    reader.readAsDataURL(file);
  };

  // Handle avatar removal
  const handleRemoveAvatar = () => {
    setAvatarUrl(null);
    localStorage.removeItem("userAvatar");
    toast.success("Avatar removed");
  };

  // Generate avatar initials from name
  const getInitials = (name: string) => {
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

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
          {/* Profile Section with Avatar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-card rounded-lg border border-border p-6"
          >
            <h2 className="font-semibold text-lg mb-6">Profile</h2>

            {/* Avatar Upload */}
            <div className="flex items-center gap-6 mb-6">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="relative group"
              >
                <div className="w-24 h-24 rounded-full border-4 border-background shadow-lg overflow-hidden bg-lime-500 flex items-center justify-center">
                  {avatarUrl ? (
                    <img src={avatarUrl} alt={userName} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-white text-xl font-bold">
                      {getInitials(userName)}
                    </span>
                  )}
                </div>

                {/* Upload Overlay */}
                <label
                  htmlFor="avatar-upload"
                  className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                >
                  <Camera className="w-6 h-6 text-white" />
                </label>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
              </motion.div>

              <div className="flex-1">
                <h3 className="font-semibold text-foreground mb-1">Profile Photo</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Upload a new avatar. JPG, PNG or GIF. Max 2MB.
                </p>
                <div className="flex items-center gap-2">
                  <label
                    htmlFor="avatar-upload"
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors cursor-pointer text-sm font-medium inline-flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    Upload New
                  </label>
                  {avatarUrl && (
                    <button
                      onClick={handleRemoveAvatar}
                      className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-sm font-medium"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Display Name</label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => {
                    setUserName(e.target.value);
                    localStorage.setItem("userName", e.target.value);
                  }}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  value={userEmail}
                  onChange={(e) => {
                    setUserEmail(e.target.value);
                    localStorage.setItem("userEmail", e.target.value);
                  }}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
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
                { key: "notifications", label: "Push Notifications", desc: "Receive notifications for task updates and mentions" },
                { key: "emailAlerts", label: "Email Alerts", desc: "Get email notifications for important updates" },
                { key: "weeklyReport", label: "Weekly Summary Report", desc: "Receive a weekly summary of your activity" },
              ].map((setting) => (
                <div key={setting.key} className="flex items-start justify-between py-2">
                  <div>
                    <span className="font-medium text-foreground">{setting.label}</span>
                    <p className="text-xs text-muted-foreground mt-0.5">{setting.desc}</p>
                  </div>
                  <button
                    onClick={() => handleNotificationToggle(setting.key)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings[setting.key as keyof typeof settings] ? "bg-primary" : "bg-muted"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition shadow-sm ${
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

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-card rounded-lg p-6 max-w-md w-full mx-4 border border-destructive/50 shadow-xl"
                >
                  <div className="flex items-start gap-3 mb-4">
                    <AlertTriangle className="w-6 h-6 text-destructive flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="font-semibold text-lg">Delete Account?</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        This action cannot be undone. All your data will be permanently deleted.
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => setShowDeleteConfirm(false)}
                      disabled={isDeleting}
                      className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={async () => {
                        setIsDeleting(true);
                        try {
                          await deleteMyAccount.mutateAsync();
                          toast.success("Account deleted successfully");
                          // Clear localStorage and redirect to login
                          localStorage.clear();
                          router.push("/login");
                        } catch (error) {
                          toast.error("Failed to delete account. Please try again.");
                          setIsDeleting(false);
                          setShowDeleteConfirm(false);
                        }
                      }}
                      disabled={isDeleting}
                      className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                    >
                      {isDeleting ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4" />
                          Delete Account
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={async () => {
                  setIsExporting(true);
                  try {
                    // Use fetch directly to handle JSON response
                    const response = await fetch('/api/v1/auth/me/export', {
                      headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                      },
                    });

                    if (!response.ok) {
                      throw new Error('Export failed');
                    }

                    const data = await response.json();
                    // Create blob and download
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `teamflow-export-${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    toast.success("Data exported successfully");
                  } catch (error) {
                    toast.error("Failed to export data. Please try again.");
                  } finally {
                    setIsExporting(false);
                  }
                }}
                disabled={isExporting}
                className="flex items-center justify-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
              >
                {isExporting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Export Data
                  </>
                )}
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:opacity-90 transition-opacity"
              >
                <Trash2 className="w-4 h-4" />
                Delete Account
              </motion.button>
            </div>

            <p className="text-xs text-muted-foreground mt-4">
              Export all your data as JSON or permanently delete your account and all associated data.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
