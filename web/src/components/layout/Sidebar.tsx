import { useTranslation } from "react-i18next";

import Chip from "@/components/ui/Chip";
import { useCounties } from "@/hooks/useReference";
import { useCreateSegment, useDeleteSegment, useSegments } from "@/hooks/useSegments";
import { AUCTIONS, AUC_LBL, TYPES, TYPE_LBL } from "@/lib/format";
import { useFilterStore } from "@/store/filters";
import { useToast } from "@/store/toast";

const FLAGS: { v: string; k: string; d: "g" | "a" | "r" }[] = [
  { v: "green", k: "green", d: "g" },
  { v: "yellow", k: "yellow", d: "a" },
  { v: "red", k: "red", d: "r" },
];
const ROIS = [
  { v: 20, l: "≥20%" },
  { v: 30, l: "≥30%" },
  { v: 35, l: "≥35%" },
];

export default function Sidebar() {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const f = useFilterStore();
  const { data: counties } = useCounties();
  const { data: segments } = useSegments();
  const createSegment = useCreateSegment();
  const deleteSegment = useDeleteSegment();

  const Title = ({ children }: { children: React.ReactNode }) => (
    <div className="mb-2 mt-4 px-[2px] text-xs font-extrabold uppercase tracking-wide text-ink2 first:mt-0">
      {children}
    </div>
  );

  async function saveSegment() {
    const name = window.prompt(t("f_savesegment"), `${t("f_segments")} ${(segments?.length ?? 0) + 1}`);
    if (!name) return;
    await createSegment.mutateAsync({ name, filters: f.asFilter(), alert_enabled: false });
    toast(t("seg_saved"));
  }

  return (
    <aside className="overflow-y-auto border-r border-line2 bg-paper p-[18px_16px]">
      <div className="mb-2 flex items-center justify-between">
        <Title>{t("f_filters")}</Title>
        <span className="cursor-pointer text-xs font-semibold text-accent2" onClick={f.clear}>
          {t("f_clear")}
        </span>
      </div>

      <Title>{t("f_flag")}</Title>
      <div className="flex flex-wrap gap-[7px]">
        {FLAGS.map((fl) => (
          <Chip
            key={fl.v}
            active={f.flag.includes(fl.v)}
            dot={fl.d}
            onClick={() => f.toggle("flag", fl.v)}
          >
            {t(fl.k)}
          </Chip>
        ))}
      </div>

      <Title>{t("f_county")}</Title>
      <div className="flex flex-col">
        {(counties ?? []).map((c) => (
          <label key={c.id} className="flex items-center gap-2 px-[2px] py-[5px] text-[13px]">
            <input
              type="checkbox"
              className="h-4 w-4 accent-[var(--accent)]"
              checked={f.county_id.includes(c.id)}
              onChange={() => f.toggle("county_id", c.id)}
            />
            {c.name} <span className="text-ink2">({c.opportunity_count})</span>
          </label>
        ))}
      </div>

      <Title>{t("f_auctiontype")}</Title>
      <div className="flex flex-wrap gap-[7px]">
        {AUCTIONS.map((a) => (
          <Chip key={a} active={f.auction_type.includes(a)} onClick={() => f.toggle("auction_type", a)}>
            {AUC_LBL[a]}
          </Chip>
        ))}
      </div>

      <Title>{t("f_type")}</Title>
      <div className="flex flex-wrap gap-[7px]">
        {TYPES.map((ty) => (
          <Chip key={ty} active={f.property_type.includes(ty)} onClick={() => f.toggle("property_type", ty)}>
            {TYPE_LBL[ty]}
          </Chip>
        ))}
      </div>

      <Title>{t("f_roi")}</Title>
      <div className="flex flex-wrap gap-[7px]">
        {ROIS.map((r) => (
          <Chip key={r.v} active={f.min_roi === r.v} onClick={() => f.setRoi(r.v)}>
            {r.l}
          </Chip>
        ))}
      </div>

      <Title>{t("f_segments")}</Title>
      <div>
        {(segments ?? []).length === 0 && (
          <div className="px-[2px] py-1 text-xs text-ink2">{t("no_segments")}</div>
        )}
        {(segments ?? []).map((s) => (
          <div
            key={s.id}
            className="mb-[7px] flex cursor-pointer items-center gap-2 rounded-[9px] border border-line2 px-[10px] py-2 text-[13px] hover:border-accent"
            onClick={() => f.applyFilter(s.filters)}
          >
            🔖 {s.name} <span className="text-ink2">({s.match_count})</span>
            <span
              className="ml-auto font-bold text-red"
              onClick={(e) => {
                e.stopPropagation();
                void deleteSegment.mutateAsync(s.id).then(() => toast(t("segment_removed")));
              }}
            >
              ✕
            </span>
          </div>
        ))}
        <button className="btn btn-subtle btn-sm mt-1 w-full" onClick={saveSegment}>
          + {t("f_savesegment")}
        </button>
      </div>
    </aside>
  );
}
