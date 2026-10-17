import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import Spinner from "@/components/ui/Spinner";
import { errorMessage } from "@/lib/api";
import { useChangePassword, useProfile, useUpdateProfile } from "@/hooks/useProfile";
import { useToast } from "@/store/toast";

export default function ProfilePage() {
  const { t } = useTranslation();
  const toast = useToast((s) => s.show);
  const { data, isLoading } = useProfile();
  const update = useUpdateProfile();
  const changePw = useChangePassword();

  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "" });
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (data)
      setForm({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone ?? "",
      });
  }, [data]);

  if (isLoading || !data) return <Spinner label={t("loading")} />;

  async function save() {
    setError(null);
    try {
      await update.mutateAsync(form);
      setEdit(false);
      toast(t("profile_saved"));
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function changePassword() {
    setError(null);
    try {
      await changePw.mutateAsync(pw);
      setPw({ current_password: "", new_password: "" });
      toast(t("pw_changed"));
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  // Función inline (no componente) para evitar remount y pérdida de foco.
  const field = (label: string, k: keyof typeof form) => (
    <label className="mb-[14px] block">
      <span className="fld-label">{label}</span>
      <input
        className="fld-input disabled:opacity-60"
        value={form[k]}
        disabled={!edit}
        onChange={(e) => setForm({ ...form, [k]: e.target.value })}
      />
    </label>
  );

  return (
    <div className="mx-auto max-w-[560px]">
      <h1 className="mb-[14px] text-[19px] font-bold">{t("menu_profile")}</h1>
      {error && <div className="mb-3 rounded-lg bg-red-bg px-3 py-2 text-sm text-red-tx">{error}</div>}

      <div className="card-surface mb-4 p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-bold">{t("prof_account")}</h2>
          {!edit ? (
            <button className="btn btn-subtle btn-sm" onClick={() => setEdit(true)}>
              {t("prof_edit")}
            </button>
          ) : (
            <div className="flex gap-2">
              <button className="btn btn-sm" onClick={save}>
                {t("prof_save")}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => setEdit(false)}>
                {t("prof_cancel")}
              </button>
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-x-4">
          {field(t("prof_fname"), "first_name")}
          {field(t("prof_lname"), "last_name")}
        </div>
        {field(t("prof_email"), "email")}
        {field(t("prof_phone"), "phone")}
      </div>

      <div className="card-surface p-5">
        <h2 className="mb-3 font-bold">{t("prof_security")}</h2>
        <label className="mb-[14px] block">
          <span className="fld-label">{t("current_password")}</span>
          <input
            className="fld-input"
            type="password"
            value={pw.current_password}
            onChange={(e) => setPw({ ...pw, current_password: e.target.value })}
          />
        </label>
        <label className="mb-[14px] block">
          <span className="fld-label">{t("new_password")}</span>
          <input
            className="fld-input"
            type="password"
            value={pw.new_password}
            onChange={(e) => setPw({ ...pw, new_password: e.target.value })}
          />
        </label>
        <button
          className="btn"
          disabled={!pw.current_password || pw.new_password.length < 8}
          onClick={changePassword}
        >
          {t("prof_changepw")}
        </button>
      </div>
    </div>
  );
}
