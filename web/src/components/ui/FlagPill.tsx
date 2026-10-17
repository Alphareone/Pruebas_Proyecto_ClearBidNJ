import { useTranslation } from "react-i18next";

import { flagShort } from "@/lib/format";
import type { Flag } from "@/types/api";

const COLOR: Record<string, string> = { g: "text-green", a: "text-amber", r: "text-red" };

export default function FlagPill({ flag }: { flag: Flag | null }) {
  const { t } = useTranslation();
  const s = flagShort(flag);
  const label = s === "g" ? t("flag_g") : s === "a" ? t("flag_a") : t("flag_r");
  return (
    <span className={`inline-flex items-center gap-[6px] text-xs font-bold ${COLOR[s]}`}>
      <i className={`dot ${s}`} />
      {label}
    </span>
  );
}
