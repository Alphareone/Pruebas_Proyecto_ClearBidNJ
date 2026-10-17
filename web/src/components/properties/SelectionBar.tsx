import { useTranslation } from "react-i18next";

import { runExport } from "@/hooks/useExport";
import { useSavedBatch } from "@/hooks/useSaved";
import { useToast } from "@/store/toast";

export default function SelectionBar({
  selection,
  onClear,
}: {
  selection: Set<string>;
  onClear: () => void;
}) {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const batch = useSavedBatch();

  if (selection.size === 0) return null;
  const ids = [...selection];

  async function save() {
    await batch.mutateAsync({ action: "add", property_ids: ids });
    toast(t("saved_toast"));
  }

  async function exportCsv() {
    toast(t("export_preparing"));
    const job = await runExport({ format: "csv", property_ids: ids });
    if (job.status === "completed" && job.download_url) {
      toast(t("export_ready"));
      window.open(job.download_url, "_blank");
    } else {
      toast(t("error"));
    }
  }

  return (
    <div className="mb-[14px] flex items-center gap-3 rounded-[10px] bg-accent px-[14px] py-[10px] text-white">
      <b>
        {selection.size} {t("sel_selected")}
      </b>
      <button className="btn btn-sm border border-white/30 bg-white/[.16] hover:bg-white/[.26]" onClick={save}>
        {t("sel_save")}
      </button>
      <button
        className="btn btn-sm border border-white/30 bg-white/[.16] hover:bg-white/[.26]"
        onClick={exportCsv}
      >
        {t("sel_export")}
      </button>
      <span className="ml-auto cursor-pointer text-lg opacity-85" onClick={onClear}>
        ✕
      </span>
    </div>
  );
}
