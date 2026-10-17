import { type ReactNode } from "react";

import { LANGS, setLang } from "@/i18n";
import { useTheme } from "@/store/theme";
import i18n from "@/i18n";

// Contenedor visual de las pantallas de autenticación (tarjeta centrada).
export default function AuthShell({ children }: { children: ReactNode }) {
  const theme = useTheme((s) => s.theme);
  const setTheme = useTheme((s) => s.setTheme);
  const isDark = document.documentElement.classList.contains("dark");

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#eef1f7] to-[#e3e8f2] p-4 dark:from-[#0d1117] dark:to-[#0a0d12]">
      <div className="absolute right-4 top-4 flex items-center gap-2">
        <select
          className="select-input"
          defaultValue={i18n.language}
          onChange={(e) => setLang(e.target.value)}
        >
          {LANGS.map(([c, n]) => (
            <option key={c} value={c}>
              {n}
            </option>
          ))}
        </select>
        <button
          className="iconbtn"
          onClick={() => setTheme(theme === "dark" || isDark ? "light" : "dark")}
          title="Toggle theme"
        >
          {isDark ? "☀" : "☾"}
        </button>
      </div>
      <div className="w-[400px] rounded-2xl border border-line2 bg-paper p-8 shadow-[0_12px_40px_rgba(20,26,40,.14)]">
        <div className="mb-5 text-center">
          <div className="text-[34px]">🏛️</div>
          <div className="mt-1 text-[19px] font-extrabold">ClearBid NJ</div>
        </div>
        {children}
      </div>
    </div>
  );
}
