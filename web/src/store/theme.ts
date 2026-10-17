// Store de tema (claro/oscuro/sistema) con persistencia y aplicación de clase.
import { create } from "zustand";

import type { Theme } from "@/types/api";

const KEY = "cb_theme";

function apply(theme: Theme) {
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const dark = theme === "dark" || (theme === "system" && prefersDark);
  document.documentElement.classList.toggle("dark", dark);
}

interface ThemeState {
  theme: Theme;
  setTheme: (t: Theme) => void;
}

const initial = (localStorage.getItem(KEY) as Theme) || "system";
apply(initial);

export const useTheme = create<ThemeState>((set) => ({
  theme: initial,
  setTheme: (t) => {
    localStorage.setItem(KEY, t);
    apply(t);
    set({ theme: t });
  },
}));
