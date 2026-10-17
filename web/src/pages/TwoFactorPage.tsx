import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import AuthShell from "@/components/auth/AuthShell";
import { authApi } from "@/hooks/useAuthApi";
import { errorMessage } from "@/lib/api";
import { useAuth } from "@/store/auth";
import { useToast } from "@/store/toast";

interface LocState {
  challengeId?: string;
  maskedPhone?: string | null;
}

export default function TwoFactorPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast((s) => s.show);
  const setSession = useAuth((s) => s.setSession);
  const state = (location.state as LocState) || {};

  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const refs = useRef<(HTMLInputElement | null)[]>([]);

  if (!state.challengeId) {
    return <Navigate to="/login" replace />;
  }

  function setDigit(i: number, val: string) {
    const v = val.replace(/\D/g, "").slice(-1);
    const next = [...digits];
    next[i] = v;
    setDigits(next);
    if (v && i < 5) refs.current[i + 1]?.focus();
    if (next.every((d) => d) && next.join("").length === 6) void submit(next.join(""));
  }

  function onKey(i: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Backspace" && !digits[i] && i > 0) refs.current[i - 1]?.focus();
  }

  function onPaste(e: React.ClipboardEvent) {
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (text.length === 6) {
      setDigits(text.split(""));
      void submit(text);
    }
  }

  async function submit(code: string) {
    setLoading(true);
    setError(null);
    try {
      const tokens = await authApi.verify2fa(state.challengeId!, code);
      setSession(tokens);
      navigate("/", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
      setDigits(Array(6).fill(""));
      refs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  }

  async function resend() {
    try {
      await authApi.resend2fa(state.challengeId!);
      toast(t("code_sent"));
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <AuthShell>
      <h2 className="mb-1 text-xl font-bold">{t("tfa_title")}</h2>
      <p className="mb-2 text-ink2">
        {t("tfa_sub")} <b>{state.maskedPhone || ""}</b>
      </p>

      {error && (
        <div className="mb-3 rounded-lg bg-red-bg px-3 py-2 text-sm text-red-tx">{error}</div>
      )}

      <div className="my-6 flex justify-center gap-2" onPaste={onPaste}>
        {digits.map((d, i) => (
          <input
            key={i}
            ref={(el) => (refs.current[i] = el)}
            className="h-[54px] w-[46px] rounded-[9px] border border-line bg-paper text-center text-[22px] font-bold text-ink outline-none focus:border-accent2"
            inputMode="numeric"
            maxLength={1}
            value={d}
            onChange={(e) => setDigit(i, e.target.value)}
            onKeyDown={(e) => onKey(i, e)}
            autoFocus={i === 0}
          />
        ))}
      </div>

      <button
        className="btn w-full"
        disabled={loading || digits.join("").length < 6}
        onClick={() => submit(digits.join(""))}
      >
        {loading ? t("loading") : t("tfa_verify")}
      </button>

      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="cursor-pointer font-semibold text-accent2" onClick={resend}>
          {t("tfa_resend")}
        </span>
        <span className="cursor-pointer text-ink2" onClick={() => navigate("/login")}>
          {t("tfa_change")}
        </span>
      </div>

      <p className="mt-4 text-center text-xs text-ink2">
        {/* En modo stub, el código llega por el log del backend ([SMS-STUB]). */}
        Stub: revisa el log del backend para el código.
      </p>
    </AuthShell>
  );
}
