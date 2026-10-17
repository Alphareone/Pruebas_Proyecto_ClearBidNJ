import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { County } from "@/types/api";

export function useCounties() {
  return useQuery({
    queryKey: ["counties"],
    staleTime: 5 * 60_000,
    queryFn: async (): Promise<County[]> => {
      const { data } = await api.get("/api/v1/counties");
      return data.items;
    },
  });
}
