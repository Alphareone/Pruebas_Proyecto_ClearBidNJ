import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { PropertyFilter, Segment } from "@/types/api";

export function useSegments() {
  return useQuery({
    queryKey: ["segments"],
    queryFn: async (): Promise<Segment[]> => {
      const { data } = await api.get("/api/v1/segments");
      return data.items;
    },
  });
}

export function useCreateSegment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: { name: string; filters: PropertyFilter; alert_enabled?: boolean }) => {
      const { data } = await api.post("/api/v1/segments", body);
      return data;
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["segments"] }),
  });
}

export function useDeleteSegment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/segments/${id}`);
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["segments"] }),
  });
}
