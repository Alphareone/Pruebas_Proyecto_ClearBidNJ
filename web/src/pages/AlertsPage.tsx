import { useTranslation } from "react-i18next";

import Spinner from "@/components/ui/Spinner";
import { useAlerts, useMarkAlert, useReadAllAlerts } from "@/hooks/useAlerts";
import { fdate } from "@/lib/format";

export default function AlertsPage() {
  const { t } = useTranslation();
  const { data, isLoading } = useAlerts();
  const mark = useMarkAlert();
  const readAll = useReadAllAlerts();

  if (isLoading) return <Spinner label={t("loading")} />;
  const items = data?.items ?? [];

  return (
    <div className="mx-auto max-w-[720px]">
      <div className="mb-[14px] flex items-center gap-3">
        <h1 className="text-[19px] font-bold">{t("nav_alerts")}</h1>
        {(data?.unread_count ?? 0) > 0 && (
          <span className="rounded-full bg-accent px-2 py-[2px] text-xs font-bold text-white">
            {data?.unread_count} {t("unread")}
          </span>
        )}
        <button className="btn btn-subtle btn-sm ml-auto" onClick={() => readAll.mutate()}>
          {t("mark_all_read")}
        </button>
      </div>

      {items.length === 0 ? (
        <div className="card-surface p-10 text-center text-ink2">{t("alerts_empty")}</div>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((a) => (
            <div
              key={a.id}
              className={`card-surface flex items-start gap-3 p-4 ${a.read ? "opacity-60" : ""}`}
              onClick={() => !a.read && mark.mutate({ id: a.id, read: true })}
            >
              <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${a.read ? "bg-line" : "bg-accent2"}`} />
              <div className="flex-1">
                <div className="font-semibold">{a.title}</div>
                {a.body && <div className="text-[13px] text-ink2">{a.body}</div>}
                <div className="mt-1 text-xs text-ink2">{fdate(a.created_at)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
