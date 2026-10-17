import { useTranslation } from "react-i18next";

const PROVIDERS: { id: string; label: string; bg: string; short: string }[] = [
  { id: "google", label: "Google", bg: "#ea4335", short: "G" },
  { id: "apple", label: "Apple", bg: "#000000", short: "" },
  { id: "facebook", label: "Facebook", bg: "#1877f2", short: "f" },
];

export default function OAuthButtons({ onPick }: { onPick: (provider: string) => void }) {
  const { t } = useTranslation();
  return (
    <>
      <div className="my-4 flex items-center gap-3 text-xs text-ink2">
        <span className="h-px flex-1 bg-line2" />
        {t("login_or")}
        <span className="h-px flex-1 bg-line2" />
      </div>
      {PROVIDERS.map((p) => (
        <button
          key={p.id}
          type="button"
          onClick={() => onPick(p.id)}
          className="mb-[9px] flex w-full items-center justify-center gap-[10px] rounded-[9px] border border-line bg-paper px-3 py-[10px] text-sm font-semibold text-ink hover:bg-wash"
        >
          <span
            className="flex h-5 w-5 items-center justify-center rounded-[5px] text-xs font-extrabold text-white"
            style={{ background: p.bg }}
          >
            {p.short || ""}
          </span>
          {p.label}
        </button>
      ))}
    </>
  );
}
