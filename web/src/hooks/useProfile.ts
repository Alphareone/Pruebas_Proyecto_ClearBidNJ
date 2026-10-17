import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Preferences, UserProfile } from "@/types/api";

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: async (): Promise<UserProfile> => {
      const { data } = await api.get("/api/v1/users/me");
      return data;
    },
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: Partial<Pick<UserProfile, "first_name" | "last_name" | "email" | "phone">>) => {
      const { data } = await api.patch("/api/v1/users/me", body);
      return data;
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["profile"] }),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: async (body: { current_password: string; new_password: string }) => {
      const { data } = await api.post("/api/v1/users/me/password", body);
      return data;
    },
  });
}

export function usePreferences() {
  return useQuery({
    queryKey: ["preferences"],
    queryFn: async (): Promise<Preferences> => {
      const { data } = await api.get("/api/v1/users/me/preferences");
      return data;
    },
  });
}

export function useUpdatePreferences() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: Partial<Preferences>) => {
      const { data } = await api.patch("/api/v1/users/me/preferences", body);
      return data;
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["preferences"] }),
  });
}
