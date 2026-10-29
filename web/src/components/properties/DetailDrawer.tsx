import { useState } from "react";
import { useTranslation } from "react-i18next";

import FlagPill from "@/components/ui/FlagPill";
import Spinner from "@/components/ui/Spinner";
import { useProperty } from "@/hooks/useProperties";
import { useSavedIds, useToggleSaved } from "@/hooks/useSaved";
import { AUC_LBL, fdate, flagShort, money, roiText, TYPE_LBL } from "@/lib/format";
import { useToast } from "@/store/toast";
import type { RuleResult } from "@/types/api";

type Tab = "fin" | "leg" | "fis" | "sem";
const SEVERITY_COLOR: Record<string, string> = {
  info: "var(--green)",
  warning: "var(--amber)",
  critical: "var(--red)",
};

export default function DetailDrawer({ id, onClose }: { id: string | null; onClose: () => void }) {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const [tab, setTab] = useState<Tab>("fin");
  const { data: p, isLoading } = useProperty(id);
  const { ids } = useSavedIds();
  const toggleSaved = useToggleSaved();

  const open = !!id;
  const isSaved = id ? ids.has(id) : false;

  async function save() {
    if (!id) return;
    await toggleSaved.mutateAsync({ id, saved: isSaved });
    toast(isSaved ? t("removed_saved") : t("saved_toast"));
  }

  const KV = ({ k, v, color }: { k: string; v: string; color?: string }) => (
    <div className="flex items-center justify-between border-b border-line2 py-[9px] text-[13.5px]">
      <span className="text-ink2">{k}</span>
      <span className="font-semibold" style={color ? { color } : undefined}>
        {v}
      </span>
    </div>
  );

  const TABS: [Tab, string][] = [
    ["fin", "d_fin"],
    ["leg", "d_leg"],
    ["fis", "d_fis"],
    ["sem", "d_sem"],
  ];

  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/40 transition-opacity ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
      />
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-[440px] max-w-[92vw] flex-col bg-paper shadow-[-12px_0_40px_rgba(0,0,0,.2)] transition-transform ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {isLoading || !p ? (
          <Spinner label={t("loading")} />
        ) : (
          <>
            <div className="border-b border-line2 p-[18px_20px]">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-bold">{p.address}</h2>
                  <div className="text-[13px] text-ink2">
                    {p.city}, NJ {p.zip}
                  </div>
                </div>
                <span className="cursor-pointer text-xl text-ink2" onClick={onClose}>
                  ✕
                </span>
              </div>
              <div className="mt-2">
                <FlagPill flag={p.flag} />
              </div>
            </div>

            <div className="flex gap-1 border-b border-line2 px-4 pt-2 overflow-x-auto">
              {TABS.map(([id2, lbl]) => (
                <button
                  key={id2}
                  onClick={() => setTab(id2)}
                  className={`whitespace-nowrap rounded-t-lg px-3 py-2 text-[13px] font-semibold ${
                    tab === id2 ? "border-b-2 border-accent text-ink" : "text-ink2"
                  }`}
                >
                  {t(lbl)}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto p-[16px_20px]">
              {tab === "fin" && (
                <>
                  <div className="mb-3 rounded-xl p-4 text-center" style={{ background: `var(--${flagBg(p.flag)})` }}>
                    <div className="text-3xl font-extrabold">{roiText(p.financial.estimated_roi)}</div>
                    <div className="text-xs text-ink2">{t("roi_cap")}</div>
                  </div>
                  <KV k={t("fin_opening")} v={money(p.financial.opening_price)} />
                  <KV k={t("fin_liens")} v={money(p.financial.total_liens)} />
                  <KV k={t("fin_arv")} v={money(p.financial.arv)} />
                  <KV k={t("fin_repairs")} v={money(p.financial.estimated_repairs)} />
                  <KV k={t("fin_maxbid")} v={money(p.financial.suggested_max_bid)} />
                  <KV
                    k={t("fin_profit")}
                    v={money(p.financial.potential_profit)}
                    color={`var(--${(p.financial.potential_profit ?? 0) < 0 ? "red" : "green"})`}
                  />
                </>
              )}
              {tab === "leg" && (
                <>
                  <KV k={t("leg_type")} v={p.legal.auction_type ? AUC_LBL[p.legal.auction_type] : "—"} />
                  <KV k={t("leg_date")} v={fdate(p.legal.auction_date)} />
                  <KV k={t("leg_place")} v={p.legal.location ?? "—"} />
                  <KV k={t("leg_case")} v={p.legal.case_number ?? "—"} />
                  <KV k={t("leg_title")} v={p.legal.title_status ?? "—"} />
                  <KV k={t("leg_occ")} v={p.legal.occupancy ?? "—"} />
                  <KV k={t("leg_deposit")} v={money(p.legal.required_deposit)} />
                </>
              )}
              {tab === "fis" && (
                <>
                  <KV k={t("fis_type")} v={p.property_type ? TYPE_LBL[p.property_type] : "—"} />
                  <KV k={t("fis_area")} v={p.physical.sqft ? `${p.physical.sqft} sqft` : "—"} />
                  <KV k={t("fis_lot")} v={p.physical.lot_sqft ? `${p.physical.lot_sqft} sqft` : "—"} />
                  <KV k={t("fis_beds")} v={`${p.physical.beds ?? "—"} / ${p.physical.baths ?? "—"}`} />
                  <KV k={t("fis_year")} v={p.physical.year_built ? String(p.physical.year_built) : "—"} />
                  <KV k={t("fis_cond")} v={p.physical.condition ?? "—"} />
                  <div className="mt-3 text-xs font-semibold uppercase text-ink2">{t("fis_loc")}</div>
                  <div className="text-[13px] text-ink2">
                    {p.physical.neighborhood ?? "—"}
                    {p.physical.school_rating ? ` · schools ${p.physical.school_rating}/10` : ""}
                  </div>
                </>
              )}
              {tab === "sem" && (
                <>
                  <div className="mb-3 flex items-start gap-2 rounded-xl p-3" style={{ background: `var(--${flagBg(p.flag)})` }}>
                    <i className={`dot ${flagShort(p.flag)} mt-1`} />
                    <b>
                      {flagShort(p.flag) === "g" ? t("flag_g") : flagShort(p.flag) === "a" ? t("flag_a") : t("flag_r")}
                    </b>
                  </div>
                  <div className="mb-2 text-xs font-semibold uppercase text-ink2">{t("sem_rules")}</div>
                  {(p.traffic_light?.rules ?? []).map((r: RuleResult, i: number) => (
                    <div key={i} className="mb-2 flex items-start gap-2 text-[13px]">
                      <span
                        className="mt-1 inline-block h-[9px] w-[9px] shrink-0 rounded-full"
                        style={{ background: SEVERITY_COLOR[r.severity] }}
                      />
                      <div>
                        <b>{r.title ?? r.code}</b>
                        <br />
                        <span className="text-ink2">{r.message}</span>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className="flex gap-2 border-t border-line2 p-4">
              <button className="btn flex-1" onClick={save}>
                {isSaved ? "★ " : "☆ "}
                {t("cta_save")}
              </button>
              <button className="btn btn-ghost flex-1" onClick={() => toast(t("cta_prepare"))}>
                {t("cta_prepare")}
              </button>
            </div>
          </>
        )}
      </aside>
    </>
  );
}

function flagBg(flag: string | null): string {
  const s = flagShort(flag);
  return s === "g" ? "green-bg" : s === "a" ? "amber-bg" : "red-bg";
}