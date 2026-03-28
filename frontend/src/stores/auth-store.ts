/**
 * Authentication state management with Zustand.
 */

import { create } from "zustand";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  locale: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  hydrate: () => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("takios_token") : null,
  user: typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("takios_user") || "null")
    : null,

  setAuth: (token: string, user: User) => {
    localStorage.setItem("takios_token", token);
    localStorage.setItem("takios_user", JSON.stringify(user));
    set({ token, user });
  },

  hydrate: () => {
    if (typeof window === "undefined") return;
    const token = localStorage.getItem("takios_token");
    const user = JSON.parse(localStorage.getItem("takios_user") || "null");
    set({ token, user });
  },

  logout: () => {
    localStorage.removeItem("takios_token");
    localStorage.removeItem("takios_user");
    set({ token: null, user: null });
  },

  isAuthenticated: () => !!get().token,
}));
