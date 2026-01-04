"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Loader2, AlertCircle, X } from "lucide-react";
import { useUsers, useDeleteUser } from "@/lib/query";
import { UserForm } from "@/components/team/UserForm";
import { UserCard } from "@/components/team/UserCard";
import { Button } from "@/components/ui/button";
import type { User } from "@/types";

interface ErrorState {
  show: boolean;
  message: string;
  type: "error" | "warning";
}

export default function TeamPage() {
  const { data: users, isLoading, error } = useUsers();
  const deleteUser = useDeleteUser();
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | Partial<User> | undefined>();
  const [errorState, setErrorState] = useState<ErrorState>({ show: false, message: "", type: "error" });

  const handleEdit = (user: User | Partial<User>) => {
    setEditingUser(user);
    setShowForm(true);
  };

  const showError = (message: string, type: "error" | "warning" = "error") => {
    setErrorState({ show: true, message, type });
    setTimeout(() => {
      setErrorState({ show: false, message: "", type: "error" });
    }, 5000);
  };

  const handleDelete = async (user: User | Partial<User>) => {
    if (confirm(`Are you sure you want to remove "${user.name}"? Their tasks will become unassigned.`)) {
      try {
        if (user.id) {
          await deleteUser.mutateAsync(user.id);
        }
      } catch (err: unknown) {
        console.error('Failed to delete user:', err);

        // Handle specific error messages from backend
        const error = err as { response?: { data?: { detail?: string } } };
        const detail = error?.response?.data?.detail;

        if (detail?.includes("Cannot delete last admin") || detail?.includes("last admin")) {
          showError(
            "Cannot remove the last admin. Please promote another team member to admin before removing this user.",
            "warning"
          );
        } else if (detail?.includes("Cannot delete yourself")) {
          showError(
            "You cannot remove yourself from the team. Please ask another admin to do this.",
            "warning"
          );
        } else {
          showError(
            detail || "Failed to remove team member. Please try again.",
            "error"
          );
        }
      }
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingUser(undefined);
  };

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <h2 className="text-lg font-bold text-red-800 dark:text-red-400 mb-2">Error loading team</h2>
          <p className="text-sm text-red-600 dark:text-red-300">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Error Alert */}
      <AnimatePresence>
        {errorState.show && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className={`mb-6 rounded-lg border p-4 flex items-start gap-3 ${
              errorState.type === "warning"
                ? "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800"
                : "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800"
            }`}
          >
            <AlertCircle
              className={`flex-shrink-0 mt-0.5 ${
                errorState.type === "warning"
                  ? "text-amber-600 dark:text-amber-400"
                  : "text-red-600 dark:text-red-400"
              }`}
              size={20}
            />
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  errorState.type === "warning"
                    ? "text-amber-800 dark:text-amber-400"
                    : "text-red-800 dark:text-red-400"
                }`}
              >
                {errorState.message}
              </p>
            </div>
            <button
              onClick={() => setErrorState({ show: false, message: "", type: "error" })}
              className={`flex-shrink-0 ${
                errorState.type === "warning"
                  ? "text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-300"
                  : "text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
              }`}
            >
              <X size={18} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between mb-8"
      >
        <div>
          <h1 className="text-3xl font-bold mb-2">Team</h1>
          <p className="text-muted-foreground">Manage your team members</p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button onClick={() => setShowForm(true)}>
            <Plus size={20} />
            Add Team Member
          </Button>
        </motion.div>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-lime-500" />
        </div>
      )}

      {/* Users Grid */}
      {!isLoading && users && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {users.length === 0 ? (
            <div className="col-span-full text-center py-20">
              <p className="text-muted-foreground mb-4">No team members yet. Add your first team member to get started.</p>
            </div>
          ) : (
            users.map((user, index: number) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <UserCard
                  user={user}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              </motion.div>
            ))
          )}
        </motion.div>
      )}

      {/* User Form Modal */}
      {showForm && (
        <UserForm
          user={editingUser}
          onClose={handleFormClose}
          onSuccess={() => {
            handleFormClose();
          }}
        />
      )}
    </div>
  );
}
