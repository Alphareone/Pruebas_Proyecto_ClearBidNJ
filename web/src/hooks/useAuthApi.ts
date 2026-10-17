// Llamadas de autenticación (no usan react-query: son acciones puntuales).
import { api } from "@/lib/api";
import type { Challenge, OAuthResponse, RegisterResponse, TokenPair } from "@/types/api";

export const authApi = {
  async login(email: string, password: string): Promise<Challenge> {
    const { data } = await api.post("/api/v1/auth/login", { email, password });
    return data;
  },
  async register(body: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    password: string;
  }): Promise<RegisterResponse> {
    const { data } = await api.post("/api/v1/auth/register", body);
    return data;
  },
  async oauth(provider: string, idToken: string): Promise<OAuthResponse> {
    const { data } = await api.post(`/api/v1/auth/oauth/${provider}`, { id_token: idToken });
    return data;
  },
  async verify2fa(challengeId: string, code: string): Promise<TokenPair> {
    const { data } = await api.post("/api/v1/auth/2fa/verify", {
      challenge_id: challengeId,
      code,
    });
    return data;
  },
  async resend2fa(challengeId: string): Promise<{ sent: boolean; expires_in: number }> {
    const { data } = await api.post("/api/v1/auth/2fa/send", { challenge_id: challengeId });
    return data;
  },
};
