import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { PropertyFilter, SavedItem } from "@/types/api";

export function useSaved() {
  return useQuery({
    queryKey: ["saved"],
    queryFn: async (): Promise<SavedItem[]> => {
      const { data } = await api.get("/api/v1/saved");
      return data.items;
    },
  });
}

export function useSavedIds() {
  const q = useSaved();
  return { ...q, ids: new Set((q.data ?? []).map((s) => s.id)) };
}

export function useToggleSaved() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, saved }: { id: string; saved: boolean }) => {
      if (saved) await api.delete(`/api/v1/saved/${id}`);
      else await api.post("/api/v1/saved", { property_id: id });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["saved"] });
    },
  });
}

export function useSavedBatch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      action: "add" | "remove";
      property_ids?: string[];
      filters?: PropertyFilter;
    }) => {
      const { data } = await api.post("/api/v1/saved/batch", body);
      return data;
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["saved"] });
    },
  });
}
