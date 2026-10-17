import { useState } from "react";
import { useTranslation } from "react-i18next";

import DetailDrawer from "@/components/properties/DetailDrawer";
import PropertyCards from "@/components/properties/PropertyCards";
import PropertyMap from "@/components/properties/PropertyMap";
import PropertyTable from "@/components/properties/PropertyTable";
import SelectionBar from "@/components/properties/SelectionBar";
import Spinner from "@/components/ui/Spinner";
import { useProperties } from "@/hooks/useProperties";
import { useCounties } from "@/hooks/useReference";
import { useFilterStore } from "@/store/filters";

type View = "table" | "cards" | "map";

export default function DashboardPage() {
  const { t } = useTranslation();
  const f = useFilterStore();
  const { data: counties } = useCounties();
  const { data, isLoading, isError } = useProperties({
    flag: f.flag,
    county_id: f.county_id,
    auction_type: f.auction_type,
    property_type: f.property_type,
    min_roi: f.min_roi,
    q: f.q,
    sort: f.sort,
    page: f.page,
    page_size: f.page_size,
  });

  const [view, setView] = useState<View>("table");
  const [selection, setSelection] = useState<Set<string>>(new Set());
  const [openId, setOpenId] = useState<string | null>(null);

  const items = data?.items ?? [];

  const toggle = (id: string) =>
    setSelection((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  const toggleAll = () =>
    setSelection((prev) => {
      const allSel = items.length > 0 && items.every((p) => prev.has(p.id));
      const next = new Set(prev);
      items.forEach((p) => (allSel ? next.delete(p.id) : next.add(p.id)));
      return next;
    });

  const VIEWS: [View, string][] = [
    ["table", "view_table"],
    ["cards", "view_cards"],
    ["map", "view_map"],
  ];

  return (
    <div>
      <div className="mb-[14px] flex flex-wrap items-center gap-3">
        <h1 className="text-[19px] font-bold">{t("dash_title")}</h1>
        <span className="text-[13px] text-ink2">
          {data ? `${data.total} ${t("results")}` : ""}
        </span>
        <div className="ml-auto flex rounded-[9px] bg-chip p-[3px]">
          {VIEWS.map(([v, lbl]) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`rounded-[7px] px-3 py-[7px] text-[13px] font-semibold ${
                view === v ? "bg-paper text-ink shadow" : "text-ink2"
              }`}
            >
              {t(lbl)}
            </button>
          ))}
        </div>
      </div>

      <SelectionBar selection={selection} onClear={() => setSelection(new Set())} />

      {isLoading ? (
        <Spinner label={t("loading")} />
      ) : isError ? (
        <div className="card-surface p-10 text-center text-ink2">{t("error")}</div>
      ) : items.length === 0 && view !== "map" ? (
        <div className="card-surface p-10 text-center text-ink2">{t("no_results")}</div>
      ) : view === "table" ? (
        <PropertyTable
          items={items}
          counties={counties ?? []}
          selection={selection}
          onToggle={toggle}
          onToggleAll={toggleAll}
          onOpen={setOpenId}
        />
      ) : view === "cards" ? (
        <PropertyCards items={items} selection={selection} onToggle={toggle} onOpen={setOpenId} />
      ) : (
        <PropertyMap onOpen={setOpenId} />
      )}

      {/* Paginación */}
      {data && data.total_pages > 1 && view !== "map" && (
        <div className="mt-4 flex items-center justify-center gap-3 text-sm">
          <button
            className="btn btn-ghost btn-sm"
            disabled={f.page <= 1}
            onClick={() => f.setPage(f.page - 1)}
          >
            {t("prev")}
          </button>
          <span className="text-ink2">
            {t("page_of", { page: data.page, pages: data.total_pages })}
          </span>
          <button
            className="btn btn-ghost btn-sm"
            disabled={f.page >= data.total_pages}
            onClick={() => f.setPage(f.page + 1)}
          >
            {t("next")}
          </button>
        </div>
      )}

      <DetailDrawer id={openId} onClose={() => setOpenId(null)} />
    </div>
  );
}
