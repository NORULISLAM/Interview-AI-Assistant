// src/store/authStore.ts
import type { AxiosError } from "axios";
import { create, StateCreator } from "zustand";
import { persist } from "zustand/middleware";
import { api, authAPI } from "../lib/api";

export interface User {
  id: number;
  email: string;
  auth_provider: string;
  is_verified: boolean;
  auto_delete_enabled: boolean;
  retention_hours: number;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string) => Promise<void>;
  verifyToken: (token: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

function errorMessage(e: unknown, fallback = "Request failed"): string {
  const ax = e as AxiosError<any>;
  return ax?.response?.data?.error || ax?.message || fallback;
}

const createAuthSlice: StateCreator<
  AuthStore,
  [["zustand/persist", unknown]],
  [],
  AuthStore
> = (set, get) => ({
  ...initialState,

  login: async (email: string) => {
    set({ isLoading: true, error: null });
    try {
      const res = await authAPI.sendMagicLink(email);
      console.log("Magic link sent:", res.data);
      set({ isLoading: false });
    } catch (e) {
      set({ error: errorMessage(e, "Login failed"), isLoading: false });
    }
  },

  verifyToken: async (token: string) => {
    set({ isLoading: true, error: null });
    try {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const { data } = await authAPI.getMe();
      set({
        user: data as User,
        token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (e) {
      delete api.defaults.headers.common["Authorization"];
      set({
        error: errorMessage(e, "Token verification failed"),
        isLoading: false,
        isAuthenticated: false,
        token: null,
        user: null,
      });
    }
  },

  logout: () => {
    delete api.defaults.headers.common["Authorization"];
    set({ ...initialState });
  },

  checkAuth: async () => {
    const { token } = get();
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }
    set({ isLoading: true });
    try {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const { data } = await authAPI.getMe();
      set({
        user: data as User,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch {
      delete api.defaults.headers.common["Authorization"];
      set({ ...initialState });
    }
  },

  clearError: () => set({ error: null }),
});

export const useAuthStore = create<AuthStore>()(
  persist(createAuthSlice, {
    name: "auth-storage",
    version: 2, // ← bump whenever you change persisted shape
    migrate: (persisted: any, fromVersion: number): AuthStore => {
      // No-op migration (works even if previous version was undefined)
      // You can transform keys here when you change the shape.
      const base = { ...initialState, ...(persisted ?? {}) };

      // Example of migrating an older key: isLoggedIn -> isAuthenticated
      if (fromVersion < 2 && "isLoggedIn" in (persisted ?? {})) {
        base.isAuthenticated = Boolean((persisted as any).isLoggedIn);
        delete (base as any).isLoggedIn;
      }

      return base as AuthStore;
    },
    // Persist only what you need:
    partialize: (state) => ({ token: state.token, user: state.user }),
  })
);
