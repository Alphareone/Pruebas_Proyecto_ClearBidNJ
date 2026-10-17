import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import AuthShell from "@/components/auth/AuthShell";
import OAuthButtons from "@/components/auth/OAuthButtons";
import { authApi } from "@/hooks/useAuthApi";
import { errorMessage } from "@/lib/api";

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Estado para alternar entre Login y Registro
  const [isSignUp, setIsSignUp] = useState(false);

  // Campos del formulario
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isSignUp) {
        // --- REGISTRO DINÁMICO EN FASTAPI & POSTGRESQL ---
        const res = await authApi.register({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          phone,
        });

        // Redirige al 2FA tras registrarse con éxito
        navigate("/verify", {
          state: { challengeId: res.challenge_id, maskedPhone: res.masked_phone },
        });
      } else {
        // --- INICIO DE SESIÓN ---
        const challenge = await authApi.login(email, password);
        navigate("/verify", {
          state: { challengeId: challenge.challenge_id, maskedPhone: challenge.masked_phone },
        });
      }
    } catch (err) {
      setError(errorMessage(err, isSignUp ? "Error al registrar usuario" : t("invalid_credentials")));
    } finally {
      setLoading(false);
    }
  }
  async function onOAuth(provider: string) {
    setLoading(true);
    setError(null);
    try {
      const idToken = `stub:${email || `${provider}user@oauth.stub`}`;
      const res = await authApi.oauth(provider, idToken);
      navigate("/verify", {
        state: { challengeId: res.challenge_id, maskedPhone: res.masked_phone },
      });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell>
      <h2 className="mb-1 text-xl font-bold">
        {isSignUp ? "Crear cuenta" : t("login_title")}
      </h2>
      <p className="mb-5 text-ink2">
        {isSignUp ? "Ingresa tus datos para registrarte" : t("login_sub")}
      </p>

      {error && (
        <div className="mb-3 rounded-lg bg-red-bg px-3 py-2 text-sm text-red-tx">{error}</div>
      )}

      <form onSubmit={onSubmit}>
        {isSignUp && (
          <>
            <div className="mb-[14px] grid grid-cols-2 gap-2">
              <label className="block">
                <span className="fld-label">Nombre</span>
                <input
                  className="fld-input"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </label>
              <label className="block">
                <span className="fld-label">Apellido</span>
                <input
                  className="fld-input"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </label>
            </div>
            <label className="mb-[14px] block">
              <span className="fld-label">Teléfono</span>
              <input
                className="fld-input"
                type="tel"
                placeholder="+15550199"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </label>
          </>
        )}

        <label className="mb-[14px] block">
          <span className="fld-label">{t("login_email")}</span>
          <input
            className="fld-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label className="mb-[14px] block">
          <span className="fld-label">{t("login_password")}</span>
          <input
            className="fld-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete={isSignUp ? "new-password" : "current-password"}
          />
        </label>

        <button className="btn w-full" disabled={loading} type="submit">
          {loading ? t("loading") : isSignUp ? "Registrarse" : t("login_signin")}
        </button>
      </form>

      <OAuthButtons onPick={onOAuth} />

      <p className="mt-3 text-center text-sm text-ink2">
        {isSignUp ? "¿Ya tienes una cuenta?" : t("login_noaccount")}{" "}
        <span
          className="cursor-pointer font-semibold text-accent2"
          onClick={() => {
            setError(null);
            setIsSignUp(!isSignUp);
          }}
        >
          {isSignUp ? "Iniciar sesión" : t("login_signup")}
        </span>
      </p>
    </AuthShell>
  );
}