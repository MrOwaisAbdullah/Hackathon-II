'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2, CheckCircle, AlertCircle, Plus } from 'lucide-react';
import { useCreateUser, useUpdateUser } from '@/lib/query';
import type { User, UserCreate, UserUpdate } from '@/types';
import { UserRole } from '@/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface UserFormProps {
  user?: User | Partial<User>;
  onClose: () => void;
  onSuccess?: (tempPassword?: string) => void;
}

export function UserForm({ user, onClose, onSuccess }: UserFormProps) {
  const isEditing = !!user;
  const createProject = useCreateUser();
  const updateProject = useUpdateUser();

  const [formData, setFormData] = React.useState<UserCreate | UserUpdate>({
    name: user?.name || '',
    email: user?.email || '',
    role: user?.role ?? UserRole.MEMBER,
    is_project_manager: user?.is_project_manager || false,
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [touched, setTouched] = React.useState<Record<string, boolean>>({});
  const [tempPassword, setTempPassword] = React.useState<string | null>(null);

  const handleChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const handleBlur = (field: string) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    // Validate on blur
    const newErrors: Record<string, string> = {};

    if (field === 'name' && !formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }

    if (field === 'email') {
      if (!formData.email?.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email as string)) {
        newErrors.email = 'Invalid email address';
      }
    }

    setErrors((prev) => ({ ...prev, ...newErrors }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Final validation
    const newErrors: Record<string, string> = {};
    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.email?.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email as string)) {
      newErrors.email = 'Invalid email address';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setTouched({ name: true, email: true, role: true, is_project_manager: true });
      return;
    }

    try {
      if (isEditing && user) {
        await updateProject.mutateAsync({ id: user.id!, data: formData });
        onSuccess?.();
      } else {
        const result = await createProject.mutateAsync(formData as UserCreate);
        // Show temp password if returned from backend
        if (result?.temp_password) {
          setTempPassword(result.temp_password);
        }
        onSuccess?.(result?.temp_password);
      }
      if (!tempPassword) {
        onClose();
      }
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  };

  const isLoading = createProject.isPending || updateProject.isPending;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: "spring", duration: 0.3 }}
          className="bg-card sm:rounded-lg shadow-xl border border-border w-full sm:max-w-md sm:m-auto h-full sm:h-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <h2 className="text-xl font-bold text-foreground">
              {isEditing ? 'Edit Team Member' : 'Add Team Member'}
            </h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              disabled={isLoading}
            >
              <X size={20} />
            </Button>
          </div>

          {/* Temp Password Display (after creation) */}
          {tempPassword && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="p-6 bg-lime-50 dark:bg-lime-900/20 border-b border-lime-200 dark:border-lime-800"
            >
              <div className="flex items-start gap-3">
                <CheckCircle className="text-lime-600 dark:text-lime-400 mt-0.5 flex-shrink-0" size={20} />
                <div className="flex-1">
                  <h3 className="font-bold text-foreground mb-1">Team Member Added!</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Share this temporary password with the user. They'll be required to change it on first login.
                  </p>
                  <div className="bg-background border border-border rounded-lg p-3 font-mono text-sm font-bold text-foreground tracking-wider select-all">
                    {tempPassword}
                  </div>
                </div>
              </div>
              <Button
                onClick={onClose}
                className="mt-4 w-full"
              >
                Done
              </Button>
            </motion.div>
          )}

          {/* Form */}
          {!tempPassword && (
            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              {/* Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-semibold text-foreground mb-2">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  onBlur={() => handleBlur('name')}
                  placeholder="e.g. John Doe"
                  disabled={isLoading}
                  className={`w-full px-4 py-3 rounded-lg border bg-background text-foreground placeholder:text-muted-foreground transition-colors ${
                    touched.name && errors.name
                      ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500'
                      : 'border-border focus:outline-none focus:ring-2 focus:ring-lime-500'
                  }`}
                />
                {touched.name && errors.name && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-500 font-medium"
                  >
                    {errors.name}
                  </motion.p>
                )}
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-foreground mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  onBlur={() => handleBlur('email')}
                  placeholder="e.g. john@example.com"
                  disabled={isLoading}
                  className={`w-full px-4 py-3 rounded-lg border bg-background text-foreground placeholder:text-muted-foreground transition-colors ${
                    touched.email && errors.email
                      ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500'
                      : 'border-border focus:outline-none focus:ring-2 focus:ring-lime-500'
                  }`}
                />
                {touched.email && errors.email && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-500 font-medium"
                  >
                    {errors.email}
                  </motion.p>
                )}
              </div>

              {/* Role */}
              <div>
                <label htmlFor="role" className="block text-sm font-semibold text-foreground mb-2">
                  Role
                </label>
                <Select
                  value={formData.role}
                  onValueChange={(value) => handleChange('role', value as UserRole)}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={UserRole.MEMBER}>Member</SelectItem>
                    <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                  </SelectContent>
                </Select>
                <p className="mt-2 text-xs text-muted-foreground">
                  Admins can manage team members and projects. Members can only view and edit assigned tasks.
                </p>
              </div>

              {/* Project Manager Checkbox */}
              <div className="flex items-start gap-3 pt-2">
                <input
                  id="is_project_manager"
                  type="checkbox"
                  checked={formData.is_project_manager || false}
                  onChange={(e) => handleChange('is_project_manager', e.target.checked)}
                  disabled={isLoading}
                  className="mt-1 w-5 h-5 rounded border-border text-lime-500 focus:ring-2 focus:ring-lime-500"
                />
                <div className="flex-1">
                  <label htmlFor="is_project_manager" className="text-sm font-semibold text-foreground cursor-pointer">
                    Project Manager
                  </label>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Project managers can create and manage projects. Only admins can assign this role.
                  </p>
                </div>
              </div>

              {/* Warning for new users */}
              {!isEditing && (
                <div className="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                  <AlertCircle className="text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" size={18} />
                  <p className="text-sm text-foreground">
                    A temporary password will be generated and displayed after creating the user. They'll be required to change it on first login.
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onClose}
                  disabled={isLoading}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Plus size={18} className="w-4 h-4" />
                      {isEditing ? 'Save Changes' : 'Add Team Member'}
                    </>
                  )}
                </Button>
              </div>
            </form>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
