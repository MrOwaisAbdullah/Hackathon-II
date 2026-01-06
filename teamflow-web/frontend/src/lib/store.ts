/** Zustand store for UI state management. SSR-safe implementation. */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

/** Sidebar state */
export interface SidebarState {
  isCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

/** Theme state */
export interface ThemeState {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

/** Modal state */
export interface ModalState {
  isTaskDrawerOpen: boolean;
  activeTaskId: string | null;
  openTaskDrawer: (taskId?: string) => void;
  closeTaskDrawer: () => void;
}

/** Combined UI store */
export interface UIStore extends SidebarState, ThemeState, ModalState {}

/** SSR-safe storage that only accesses localStorage on client */
const storage = {
  getItem: (name: string) => {
    if (typeof window === 'undefined') return null;
    const str = localStorage.getItem(name);
    if (!str) return null;
    try {
      return JSON.parse(str);
    } catch {
      return null;
    }
  },
  setItem: (name: string, value: unknown) => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(name, JSON.stringify(value));
  },
  removeItem: (name: string) => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(name);
  },
};

/** Create the UI store with persistence for sidebar and theme */
export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      // Sidebar state
      isCollapsed: false,
      toggleSidebar: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ isCollapsed: collapsed }),

      // Theme state
      theme: 'light',
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      setTheme: (theme) => set({ theme }),

      // Modal state
      isTaskDrawerOpen: false,
      activeTaskId: null,
      openTaskDrawer: (taskId) => set({ isTaskDrawerOpen: true, activeTaskId: taskId ?? null }),
      closeTaskDrawer: () => set({ isTaskDrawerOpen: false, activeTaskId: null }),
    }),
    {
      name: 'teamflow-ui-storage',
      storage: createJSONStorage(() => storage),
      partialize: (state) => ({
        isCollapsed: state.isCollapsed,
        theme: state.theme,
      }),
    }
  )
);

/** Hooks for specific UI slices */
export const useSidebar = () => useUIStore((state) => ({
  isCollapsed: state.isCollapsed,
  toggleSidebar: state.toggleSidebar,
  setSidebarCollapsed: state.setSidebarCollapsed,
}));

export const useTheme = () => useUIStore((state) => ({
  theme: state.theme,
  toggleTheme: state.toggleTheme,
  setTheme: state.setTheme,
}));

export const useModal = () => useUIStore((state) => ({
  isTaskDrawerOpen: state.isTaskDrawerOpen,
  activeTaskId: state.activeTaskId,
  openTaskDrawer: state.openTaskDrawer,
  closeTaskDrawer: state.closeTaskDrawer,
}));
