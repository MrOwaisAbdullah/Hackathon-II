'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { MoreHorizontal, Edit, Trash2, Shield } from 'lucide-react';
import type { User } from '@/types';
import { UserRole } from '@/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';

interface UserCardProps {
  user: User | Partial<User>;
  onEdit: (user: User | Partial<User>) => void;
  onDelete: (user: User | Partial<User>) => void;
}

export function UserCard({ user, onEdit, onDelete }: UserCardProps) {
  const [showMenu, setShowMenu] = React.useState(false);
  const [isDark, setIsDark] = React.useState(false);

  // Detect dark mode
  React.useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  // Role badge styles - theme aware
  const getRoleStyle = (role: UserRole) => {
    const styles = {
      [UserRole.ADMIN]: {
        label: 'Admin',
        light: { backgroundColor: '#f3e8ff', color: '#5b21b6' },
        dark: { backgroundColor: 'rgba(91, 33, 182, 0.3)', color: '#a78bfa' },
      },
      [UserRole.MEMBER]: {
        label: 'Member',
        light: { backgroundColor: '#dbeafe', color: '#1e3a8a' },
        dark: { backgroundColor: 'rgba(30, 58, 138, 0.3)', color: '#60a5fa' },
      },
      [UserRole.VIEWER]: {
        label: 'Viewer',
        light: { backgroundColor: '#f3f4f6', color: '#1f2937' },
        dark: { backgroundColor: 'rgba(31, 41, 55, 0.5)', color: '#d1d5db' },
      },
    };
    return styles[role as keyof typeof styles] || styles[UserRole.MEMBER];
  };

  // PM badge style
  const pmStyle = {
    light: { backgroundColor: '#fef9c3', color: '#78350f' },
    dark: { backgroundColor: 'rgba(120, 53, 15, 0.3)', color: '#fde047' },
  };

  // Inactive badge style
  const inactiveStyle = {
    light: { backgroundColor: '#f3f4f6', color: '#6b7280' },
    dark: { backgroundColor: 'rgba(55, 65, 81, 0.5)', color: '#9ca3af' },
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      '#84cc16', // lime-500
      '#3b82f6', // blue-500
      '#a855f7', // purple-500
      '#f59e0b', // amber-500
      '#ef4444', // red-500
      '#06b6d4', // cyan-500
      '#ec4899', // pink-500
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const roleStyle = getRoleStyle(user.role as UserRole);
  const finalRoleStyle = isDark ? roleStyle.dark : roleStyle.light;
  const finalPmStyle = isDark ? pmStyle.dark : pmStyle.light;
  const finalInactiveStyle = isDark ? inactiveStyle.dark : inactiveStyle.light;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="group relative bg-card rounded-xl border border-border hover:shadow-lg hover:border-lime-500/50 transition-all"
    >
      <div className="p-4 md:p-6">
        <div className="flex items-start justify-between">
          {/* User Info */}
          <div className="flex items-start gap-4 flex-1">
            {/* Avatar */}
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: getAvatarColor(user.name || 'User') }}
            >
              <span className="text-white font-bold text-sm">{getInitials(user.name || 'User')}</span>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <h3 className="font-bold text-base text-foreground leading-none">
                  {user.name}
                </h3>
                {user.is_project_manager && (
                  <span
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide"
                    style={finalPmStyle}
                  >
                    <Shield size={10} />
                    PM
                  </span>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{user.email}</p>

              {/* Badges */}
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span
                  className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
                  style={finalRoleStyle}
                >
                  {roleStyle.label}
                </span>
                {!user.active && (
                  <span
                    className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
                    style={finalInactiveStyle}
                  >
                    Inactive
                  </span>
                )}
              </div>

              {/* Meta Info */}
              <div className="mt-3 text-xs text-muted-foreground">
                Added {new Date(user.created_at || '').toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Actions Menu */}
          <DropdownMenu open={showMenu} onOpenChange={setShowMenu}>
            <DropdownMenuTrigger asChild>
              <motion.button
                whileHover={{ rotate: 90, scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 text-muted-foreground hover:text-foreground hover:bg-muted"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreHorizontal size={16} strokeWidth={2.5} />
              </motion.button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-48"
              sideOffset={5}
              onClick={(e) => e.stopPropagation()}
            >
              <DropdownMenuLabel className="text-xs font-semibold text-muted-foreground">
                Member Actions
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(user);
                }}
                className="cursor-pointer"
              >
                <Edit className="w-4 h-4 mr-2 text-lime-600" />
                <span>Edit Member</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(user);
                }}
                className="cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50 dark:focus:bg-rose-950/20"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                <span>Remove Member</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </motion.div>
  );
}
