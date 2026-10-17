// Store de autenticación (Zustand). Guarda el usuario y expone login/logout.
import { create } from "zustand";

import { api } from "@/lib/api";
import { tokenStore } from "@/lib/tokens";
import type { TokenPair, UserPublic } from "@/types/api";

interface AuthState {
  user: UserPublic | null;
  isAuthenticated: boolean;
  setSession: (tokens: TokenPair) => void;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!tokenStore.getAccess(),
  setSession: (tokens) => {
    tokenStore.set(tokens.access_token, tokens.refresh_token);
    set({ user: tokens.user ?? null, isAuthenticated: true });
  },
  logout: () => {
    const refresh = tokenStore.getRefresh();
    if (refresh) api.post("/api/v1/auth/logout", { refresh_token: refresh }).catch(() => {});
    tokenStore.clear();
    set({ user: null, isAuthenticated: false });
  },
  // Al recargar, si hay token recupera el perfil.
  hydrate: async () => {
    if (!tokenStore.getAccess()) return;
    try {
      const { data } = await api.get("/api/v1/users/me");
      set({
        user: {
          id: data.id,
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          role: data.role,
        },
        isAuthenticated: true,
      });
    } catch {
      tokenStore.clear();
      set({ user: null, isAuthenticated: false });
    }
  },
}));
