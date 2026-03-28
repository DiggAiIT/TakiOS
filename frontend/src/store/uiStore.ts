import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'

interface UIState {
  sidebarOpen: boolean;
  activeModal: string | null;
  theme: Theme;
  toggleSidebar: () => void;
  setModal: (modalName: string | null) => void;
  setTheme: (theme: Theme) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      activeModal: null,
      theme: 'system',
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setModal: (modalName) => set({ activeModal: modalName }),
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'takios-ui' }
  )
)
