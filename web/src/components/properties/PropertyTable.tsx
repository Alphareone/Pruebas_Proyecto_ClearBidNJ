import { useTranslation } from "react-i18next";

import FlagPill from "@/components/ui/FlagPill";
import { fdate, money, roiClass, roiText, TYPE_LBL } from "@/lib/format";
import { useFilterStore } from "@/store/filters";
import type { County, PropertyListItem } from "@/types/api";

const COLS: [string, string, boolean][] = [
  ["flag", "col_flag", false],
  ["address", "col_address", false],
  ["county", "col_county", false],
  ["type", "col_type", false],
  ["opening", "col_opening", true],
  ["arv", "col_arv", true],
  ["roi", "col_roi", true],
  ["auction", "col_auction", false],
];

// Mapea columna -> clave de sort del backend (solo las soportadas).
const SORT_MAP: Record<string, string | null> = {
  opening: "opening_asc",
  roi: "roi_desc",
  auction: "auction_date",
};

export default function PropertyTable({
  items,
  counties,
  selection,
  onToggle,
  onToggleAll,
  onOpen,
}: {
  items: PropertyListItem[];
  counties: County[];
  selection: Set<string>;
  onToggle: (id: string) => void;
  onToggleAll: () => void;
  onOpen: (id: string) => void;
}) {
  const { t } = useTranslation();
  const sort = useFilterStore((s) => s.sort);
  const setSort = useFilterStore((s) => s.setSort);
  const countyName = (id: string) => counties.find((c) => c.id === id)?.name ?? id;
  const allSel = items.length > 0 && items.every((p) => selection.has(p.id));

  function sortBy(col: string) {
    const key = SORT_MAP[col];
    if (!key) return;
    // alterna asc/desc en 'opening'
    if (col === "opening") setSort(sort === "opening_asc" ? "opening_desc" : "opening_asc");
    else setSort(key);
  }

  const arrow = (col: string) => {
    const key = SORT_MAP[col];
    if (!key) return null;
    if (col === "opening" && sort.startsWith("opening"))
      return <span className="ml-[3px] text-accent2">{sort === "opening_asc" ? "▲" : "▼"}</span>;
    if (sort === key) return <span className="ml-[3px] text-accent2">▼</span>;
    return null;
  };

  return (
    <div className="card-surface overflow-hidden">
      <table className="w-full border-collapse text-[13.5px]">
        <thead>
          <tr>
            <th className="w-[34px] border-b border-line2 bg-wash p-[11px_12px]">
              <input
                type="checkbox"
                className="h-4 w-4 accent-[var(--accent)]"
                checked={allSel}
                onChange={onToggleAll}
              />
            </th>
            {COLS.map(([k, lbl, num]) => (
              <th
                key={k}
                onClick={() => sortBy(k)}
                className={`whitespace-nowrap border-b border-line2 bg-wash p-[11px_12px] text-xs font-bold text-ink2 ${
                  num ? "text-right" : "text-left"
                } ${SORT_MAP[k] ? "cursor-pointer select-none" : ""}`}
              >
                {t(lbl)}
                {arrow(k)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr
              key={p.id}
              onClick={() => onOpen(p.id)}
              className={`cursor-pointer border-b border-line2 hover:bg-wash ${
                selection.has(p.id) ? "bg-[color-mix(in_srgb,var(--accent)_8%,transparent)]" : ""
              }`}
            >
              <td className="p-[11px_12px]" onClick={(e) => e.stopPropagation()}>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-[var(--accent)]"
                  checked={selection.has(p.id)}
                  onChange={() => onToggle(p.id)}
                />
              </td>
              <td className="p-[11px_12px]">
                <FlagPill flag={p.flag} />
              </td>
              <td className="p-[11px_12px]">
                <b className="block">{p.address}</b>
                <span className="text-xs text-ink2">
                  {p.city}, NJ {p.zip}
                </span>
              </td>
              <td className="p-[11px_12px]">{countyName(p.county_id)}</td>
              <td className="p-[11px_12px]">{p.property_type ? TYPE_LBL[p.property_type] : "—"}</td>
              <td className="p-[11px_12px] text-right tabular-nums">{money(p.opening_price)}</td>
              <td className="p-[11px_12px] text-right tabular-nums">{money(p.estimated_value)}</td>
              <td className="p-[11px_12px] text-right tabular-nums">
                <span className={roiClass(p.estimated_roi)}>{roiText(p.estimated_roi)}</span>
              </td>
              <td className="p-[11px_12px]">{fdate(p.auction_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
