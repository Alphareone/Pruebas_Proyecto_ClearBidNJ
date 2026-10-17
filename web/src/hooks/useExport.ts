import { api } from "@/lib/api";
import type { ExportJob, PropertyFilter } from "@/types/api";

// Inicia una exportación y hace polling hasta que termina; devuelve la URL.
export async function runExport(body: {
  format: "csv" | "xlsx";
  property_ids?: string[];
  filters?: PropertyFilter;
  columns?: string[];
}): Promise<ExportJob> {
  const { data } = await api.post("/api/v1/properties/export", body);
  let job: ExportJob = data;
  for (let i = 0; i < 20 && (job.status === "queued" || job.status === "processing"); i++) {
    await new Promise((r) => setTimeout(r, 800));
    const res = await api.get(`/api/v1/exports/${job.job_id}`);
    job = res.data;
  }
  return job;
}
