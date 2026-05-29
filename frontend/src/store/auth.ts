import { create } from "zustand";
import { api, tokenStore } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthState {
  user: User | null;
  loading: boolean;
  initialized: boolean;
  hydrate: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: false,
  initialized: false,

  hydrate: async () => {
    if (!tokenStore.access) {
      set({ initialized: true });
      return;
    }
    try {
      const user = await api.me();
      set({ user, initialized: true });
    } catch {
      tokenStore.clear();
      set({ user: null, initialized: true });
    }
  },

  login: async (email, password) => {
    set({ loading: true });
    try {
      tokenStore.set(await api.login(email, password));
      set({ user: await api.me() });
    } finally {
      set({ loading: false });
    }
  },

  register: async (email, password, fullName) => {
    set({ loading: true });
    try {
      tokenStore.set(await api.register(email, password, fullName));
      set({ user: await api.me() });
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    try {
      await api.logout();
    } catch {
      /* ignore */
    }
    tokenStore.clear();
    set({ user: null });
  },
}));
