import { useState } from "react";
import { useTranslation } from "react-i18next";

import Spinner from "@/components/ui/Spinner";
import { useAddCoverage, useCoverage, useRemoveCoverage } from "@/hooks/useCoverage";
import { useUpdatePreferences } from "@/hooks/useProfile";
import { useCounties } from "@/hooks/useReference";
import i18n, { LANGS, setLang } from "@/i18n";
import { errorMessage } from "@/lib/api";
import { useTheme } from "@/store/theme";
import { useToast } from "@/store/toast";
import type { Language } from "@/types/api";

export default function SettingsPage() {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const theme = useTheme((s) => s.theme);
  const setTheme = useTheme((s) => s.setTheme);
  const { data: coverage, isLoading } = useCoverage();
  const { data: counties } = useCounties();
  const addCoverage = useAddCoverage();
  const removeCoverage = useRemoveCoverage();
  const updatePrefs = useUpdatePreferences();

  const [newZone, setNewZone] = useState("");
  const isDark = document.documentElement.classList.contains("dark");

  function onLang(code: string) {
    setLang(code);
    void updatePrefs.mutateAsync({ language: code as Language }).catch(() => {});
  }

  function onTheme(dark: boolean) {
    const next = dark ? "dark" : "light";
    setTheme(next);
    void updatePrefs.mutateAsync({ theme: next }).catch(() => {});
  }

  async function addZone() {
    const val = newZone.trim();
    if (!val) return;
    try {
      // Si es un county por nombre, resuelve el id; si son 5 dígitos, es ZIP.
      if (/^\d{5}$/.test(val)) {
        await addCoverage.mutateAsync({ type: "zip", ref_id: val });
      } else {
        const county = counties?.find((c) => c.name.toLowerCase() === val.toLowerCase());
        if (!county) {
          toast(t("error"));
          return;
        }
        await addCoverage.mutateAsync({ type: "county", ref_id: county.id });
      }
      setNewZone("");
      toast(t("coverage_added"));
    } catch (err) {
      toast(errorMessage(err));
    }
  }

  return (
    <div className="mx-auto max-w-[560px]">
      <h1 className="mb-[14px] text-[19px] font-bold">{t("menu_settings")}</h1>

      <div className="card-surface mb-4 p-5">
        <h2 className="mb-3 font-bold">{t("set_appearance")}</h2>
        <div className="mb-4 flex items-center justify-between">
          <span className="fld-label mb-0">{t("set_language")}</span>
          <select className="select-input" value={i18n.language} onChange={(e) => onLang(e.target.value)}>
            {LANGS.map(([c, n]) => (
              <option key={c} value={c}>
                {n}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <div className="font-semibold">{t("set_darkmode")}</div>
            <div className="text-xs text-ink2">{t("set_darkmode_sub")}</div>
          </div>
          <button
            className={`relative h-6 w-11 rounded-full transition-colors ${
              isDark ? "bg-accent" : "bg-line"
            }`}
            onClick={() => onTheme(!isDark)}
          >
            <span
              className={`absolute top-[2px] h-5 w-5 rounded-full bg-white transition-all ${
                isDark ? "left-[22px]" : "left-[2px]"
              }`}
            />
          </button>
        </div>
        <div className="mt-2 text-xs text-ink2">
          {t("set_darkmode")}: {theme}
        </div>
      </div>

      <div className="card-surface p-5">
        <h2 className="font-bold">{t("set_coverage")}</h2>
        <p className="mb-3 text-xs text-ink2">{t("set_coverage_sub")}</p>
        {isLoading ? (
          <Spinner />
        ) : (
          <div className="mb-3 flex flex-col gap-2">
            {(coverage ?? []).map((z) => (
              <div
                key={z.id}
                className="flex items-center gap-2 rounded-[9px] border border-line2 px-3 py-2 text-[13px]"
              >
                📍 {z.label ?? z.ref_id}
                <span
                  className="ml-auto cursor-pointer font-bold text-red"
                  onClick={() =>
                    void removeCoverage.mutateAsync(z.id).then(() => toast(t("coverage_removed")))
                  }
                >
                  ✕
                </span>
              </div>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <input
            className="fld-input"
            placeholder={t("add_ph")}
            value={newZone}
            onChange={(e) => setNewZone(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addZone()}
          />
          <button className="btn" onClick={addZone}>
            {t("add")}
          </button>
        </div>
      </div>
    </div>
  );
}
