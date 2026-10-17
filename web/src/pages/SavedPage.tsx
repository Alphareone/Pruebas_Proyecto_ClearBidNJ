import { useState } from "react";
import { useTranslation } from "react-i18next";

import DetailDrawer from "@/components/properties/DetailDrawer";
import FlagPill from "@/components/ui/FlagPill";
import Spinner from "@/components/ui/Spinner";
import { useSaved, useToggleSaved } from "@/hooks/useSaved";
import { fdate, money } from "@/lib/format";
import { useToast } from "@/store/toast";

export default function SavedPage() {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const { data, isLoading } = useSaved();
  const toggleSaved = useToggleSaved();
  const [openId, setOpenId] = useState<string | null>(null);

  if (isLoading) return <Spinner label={t("loading")} />;
  const items = data ?? [];

  return (
    <div>
      <h1 className="mb-[14px] text-[19px] font-bold">{t("nav_saved")}</h1>
      {items.length === 0 ? (
        <div className="card-surface p-10 text-center text-ink2">{t("saved_empty")}</div>
      ) : (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-[14px]">
          {items.map((p) => (
            <div key={p.id} className="card-surface cursor-pointer p-4" onClick={() => setOpenId(p.id)}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-bold">{p.address}</div>
                  <div className="text-xs text-ink2">{p.city}, NJ</div>
                </div>
                <FlagPill flag={p.flag} />
              </div>
              <div className="mt-3 flex items-center justify-between text-[13px]">
                <span className="text-ink2">
                  {t("col_opening")}: <b className="text-ink">{money(p.opening_price)}</b>
                </span>
                <span className="text-xs text-ink2">{fdate(p.saved_at)}</span>
              </div>
              <button
                className="btn btn-ghost btn-sm mt-3 w-full"
                onClick={(e) => {
                  e.stopPropagation();
                  void toggleSaved
                    .mutateAsync({ id: p.id, saved: true })
                    .then(() => toast(t("removed_saved")));
                }}
              >
                ★ {t("cta_save")}
              </button>
            </div>
          ))}
        </div>
      )}
      <DetailDrawer id={openId} onClose={() => setOpenId(null)} />
    </div>
  );
}
