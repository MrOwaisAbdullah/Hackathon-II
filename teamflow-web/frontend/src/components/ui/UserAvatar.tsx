'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface UserAvatarProps {
  name?: string;
  email?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showRing?: boolean;
}

export function UserAvatar({
  name = 'User',
  className,
  size = 'md',
  showRing = false,
}: UserAvatarProps) {
  const [avatarUrl, setAvatarUrl] = React.useState<string | null>(null);
  const [userName, setUserName] = React.useState(name);

  // Load avatar and name from localStorage
  React.useEffect(() => {
    const storedAvatar = localStorage.getItem('userAvatar');
    if (storedAvatar) {
      setAvatarUrl(storedAvatar);
    }

    const storedName = localStorage.getItem('userName');
    if (storedName) {
      setUserName(storedName);
    }
  }, []);

  // Generate initials from name
  const getInitials = (name: string) => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base',
    xl: 'w-12 h-12 text-lg',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={cn(
        'relative rounded-full overflow-hidden flex items-center justify-center font-bold',
        'bg-lime-500 text-white shadow-sm',
        sizeClasses[size],
        showRing && 'ring-2 ring-lime-500/50 ring-offset-2 ring-offset-background',
        className
      )}
    >
      {avatarUrl ? (
        <img
          src={avatarUrl}
          alt={userName}
          className="w-full h-full object-cover"
        />
      ) : (
        <span>{getInitials(userName)}</span>
      )}
    </motion.div>
  );
}

interface UserAvatarWithMenuProps extends UserAvatarProps {
  showMenu?: boolean;
  onAvatarClick?: () => void;
  menuItems?: Array<{
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  }>;
}

export function UserAvatarWithMenu({
  name,
  email,
  className,
  size = 'md',
  showMenu = true,
  onAvatarClick,
  menuItems = [],
}: UserAvatarWithMenuProps) {
  const [showDropdown, setShowDropdown] = React.useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => {
          onAvatarClick?.();
          if (showMenu) {
            setShowDropdown(!showDropdown);
          }
        }}
        className="focus:outline-none focus:ring-2 focus:ring-lime-500 rounded-full"
      >
        <UserAvatar
          name={name}
          email={email}
          className={className}
          size={size}
          showRing={showDropdown}
        />
      </button>

      {showMenu && showDropdown && menuItems.length > 0 && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowDropdown(false)}
          />
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute right-0 top-full mt-2 z-20 w-48 bg-card rounded-lg border border-border shadow-lg py-1"
          >
            {menuItems.map((item, index) => (
              <button
                key={index}
                onClick={() => {
                  item.onClick();
                  setShowDropdown(false);
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted flex items-center gap-2 transition-colors"
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </motion.div>
        </>
      )}
    </div>
  );
}
