import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { AlertList, AlertSettings } from "@/types/api";

export function useAlerts(unread?: boolean) {
  return useQuery({
    queryKey: ["alerts", unread],
    queryFn: async (): Promise<AlertList> => {
      const p = unread ? "?unread=true" : "";
      const { data } = await api.get(`/api/v1/alerts${p}`);
      return data;
    },
  });
}

export function useMarkAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, read }: { id: string; read: boolean }) => {
      await api.patch(`/api/v1/alerts/${id}`, { read });
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["alerts"] }),
  });
}

export function useReadAllAlerts() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.post("/api/v1/alerts/read-all");
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["alerts"] }),
  });
}

export function useAlertSettings() {
  return useQuery({
    queryKey: ["alert-settings"],
    queryFn: async (): Promise<AlertSettings> => {
      const { data } = await api.get("/api/v1/alerts/settings");
      return data;
    },
  });
}
