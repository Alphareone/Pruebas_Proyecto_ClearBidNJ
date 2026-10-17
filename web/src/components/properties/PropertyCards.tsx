import { useTranslation } from "react-i18next";

import FlagPill from "@/components/ui/FlagPill";
import { money, roiClass, roiText, TYPE_LBL } from "@/lib/format";
import type { PropertyListItem } from "@/types/api";

export default function PropertyCards({
  items,
  selection,
  onToggle,
  onOpen,
}: {
  items: PropertyListItem[];
  selection: Set<string>;
  onToggle: (id: string) => void;
  onOpen: (id: string) => void;
}) {
  const { t } = useTranslation();
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-[14px]">
      {items.map((p) => (
        <div
          key={p.id}
          onClick={() => onOpen(p.id)}
          className={`relative cursor-pointer overflow-hidden rounded-xl border border-line2 bg-paper ${
            selection.has(p.id) ? "outline outline-2 outline-accent" : ""
          }`}
        >
          <div className="relative flex h-[120px] items-center justify-center bg-[repeating-linear-gradient(45deg,var(--grid1)_0_12px,var(--grid2)_12px_24px)] text-xs text-ink2">
            <input
              type="checkbox"
              className="absolute left-[9px] top-[9px] h-[18px] w-[18px] accent-[var(--accent)]"
              checked={selection.has(p.id)}
              onClick={(e) => e.stopPropagation()}
              onChange={() => onToggle(p.id)}
            />
            {t("gallery")}
            <span className="absolute right-[9px] top-[9px] rounded-2xl bg-paper px-[9px] py-[3px] shadow">
              <FlagPill flag={p.flag} />
            </span>
          </div>
          <div className="p-[11px_13px]">
            <div className="font-bold">{p.address}</div>
            <div className="mt-[1px] text-xs text-ink2">
              {p.city}, NJ {p.zip} · {p.property_type ? TYPE_LBL[p.property_type] : "—"}
            </div>
            <div className="mt-[9px] flex gap-[14px]">
              <Stat k={t("col_opening")} v={money(p.opening_price)} />
              <Stat k={t("col_arv")} v={money(p.estimated_value)} />
              <Stat k="ROI" v={roiText(p.estimated_roi)} cls={roiClass(p.estimated_roi)} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function Stat({ k, v, cls }: { k: string; v: string; cls?: string }) {
  return (
    <div>
      <div className="text-[10px] uppercase text-ink2">{k}</div>
      <div className={`text-[13px] font-bold ${cls ?? ""}`}>{v}</div>
    </div>
  );
}
