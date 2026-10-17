import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, useNavigate } from "react-router-dom";

import i18n, { LANGS, setLang } from "@/i18n";
import { useAuth } from "@/store/auth";
import { useTheme } from "@/store/theme";
import { useFilterStore } from "@/store/filters";

export default function TopBar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const theme = useTheme((s) => s.theme);
  const setTheme = useTheme((s) => s.setTheme);
  const q = useFilterStore((s) => s.q);
  const setQ = useFilterStore((s) => s.setQ);

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const isDark = document.documentElement.classList.contains("dark");
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-[13.5px] font-semibold ${
      isActive ? "bg-chip text-ink" : "text-ink2 hover:bg-wash"
    }`;

  const initials = user ? (user.first_name[0] ?? "") + (user.last_name[0] ?? "") : "?";

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-[18px] border-b border-line2 bg-paper px-5">
      <div className="flex items-center gap-2 text-base font-extrabold">🏛️ ClearBid NJ</div>

      <nav className="ml-1 flex gap-1">
        <NavLink to="/" end className={navClass}>
          {t("nav_dashboard")}
        </NavLink>
        <NavLink to="/saved" className={navClass}>
          {t("nav_saved")}
        </NavLink>
        <NavLink to="/alerts" className={navClass}>
          {t("nav_alerts")}
        </NavLink>
      </nav>

      <div className="flex max-w-[360px] flex-1 items-center gap-2 rounded-[9px] border border-line bg-wash px-3">
        <span className="text-ink2">🔍</span>
        <input
          className="w-full bg-transparent py-[9px] text-[13.5px] text-ink outline-none"
          placeholder={t("search_ph")}
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      <div className="ml-auto flex items-center gap-[10px]">
        <select
          className="select-input"
          value={i18n.language}
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
          title="Theme"
          onClick={() => setTheme(theme === "dark" || isDark ? "light" : "dark")}
        >
          {isDark ? "☀" : "☾"}
        </button>

        <div className="relative" ref={menuRef}>
          <div
            className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full bg-chip text-base uppercase"
            onClick={() => setMenuOpen((o) => !o)}
          >
            {initials}
          </div>
          {menuOpen && (
            <div className="absolute right-0 top-11 z-40 min-w-[190px] rounded-xl border border-line2 bg-paper p-[6px] shadow-[0_10px_30px_rgba(0,0,0,.15)]">
              <div className="mb-1 border-b border-line2 px-3 py-[10px]">
                <b className="block">
                  {user?.first_name} {user?.last_name}
                </b>
                <span className="text-xs text-ink2">{user?.email}</span>
              </div>
              <div
                className="cursor-pointer rounded-lg px-3 py-[9px] text-[13.5px] hover:bg-chip"
                onClick={() => {
                  setMenuOpen(false);
                  navigate("/profile");
                }}
              >
                {t("menu_profile")}
              </div>
              <div
                className="cursor-pointer rounded-lg px-3 py-[9px] text-[13.5px] hover:bg-chip"
                onClick={() => {
                  setMenuOpen(false);
                  navigate("/settings");
                }}
              >
                {t("menu_settings")}
              </div>
              <div
                className="cursor-pointer rounded-lg px-3 py-[9px] text-[13.5px] text-red hover:bg-chip"
                onClick={() => {
                  logout();
                  navigate("/login");
                }}
              >
                {t("logout")}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
