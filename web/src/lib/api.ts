// Cliente Axios con inyección de JWT y refresh automático ante 401.
import axios, {
  AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

import type { ApiError } from "@/types/api";
import { tokenStore } from "./tokens";

const baseURL = import.meta.env.VITE_API_URL || "";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

// Adjunta el access token a cada request.
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- Refresh con cola para evitar múltiples refresh simultáneos ---
let refreshing: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${baseURL}/api/v1/auth/token/refresh`, {
      refresh_token: refresh,
    });
    tokenStore.set(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    tokenStore.clear();
    return null;
  }
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;
    const isAuthCall = original?.url?.includes("/auth/");

    if (status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      refreshing = refreshing ?? doRefresh();
      const newToken = await refreshing;
      refreshing = null;
      if (newToken) {
        original.headers = { ...original.headers, Authorization: `Bearer ${newToken}` };
        return api(original);
      }
      // Sesión perdida: redirige a login.
      window.dispatchEvent(new CustomEvent("cb:logout"));
    }
    return Promise.reject(error);
  }
);

// Extrae un mensaje legible del formato de error del backend.
export function errorMessage(err: unknown, fallback = "Something went wrong"): string {
  const e = err as AxiosError<ApiError>;
  return e?.response?.data?.error?.message || e?.message || fallback;
}
