import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { CoverageItem } from "@/types/api";

export function useCoverage() {
  return useQuery({
    queryKey: ["coverage"],
    queryFn: async (): Promise<CoverageItem[]> => {
      const { data } = await api.get("/api/v1/coverage");
      return data.items;
    },
  });
}

export function useAddCoverage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: { type: "county" | "zip"; ref_id: string }) => {
      const { data } = await api.post("/api/v1/coverage", body);
      return data;
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["coverage"] }),
  });
}

export function useRemoveCoverage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/coverage/${id}`);
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["coverage"] }),
  });
}
