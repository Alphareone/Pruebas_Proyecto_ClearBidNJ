// Helpers de formato y mapeos de etiquetas.
import type { AuctionType, Flag, PropertyType } from "@/types/api";

export const TYPES: PropertyType[] = ["single_family", "condo", "multi_family", "land"];
export const TYPE_LBL: Record<string, string> = {
  single_family: "Single family",
  condo: "Condo",
  multi_family: "Multi-family",
  land: "Land",
};
export const AUCTIONS: AuctionType[] = ["sheriff_sale", "tax_lien", "tax_deed", "bank_owned"];
export const AUC_LBL: Record<string, string> = {
  sheriff_sale: "Sheriff sale",
  tax_lien: "Tax lien",
  tax_deed: "Tax deed",
  bank_owned: "Bank owned",
};

// Mapea el flag del backend (green/yellow/red) a la clase corta del wireframe.
export const flagShort = (f: Flag | string | null): "g" | "a" | "r" => {
  if (f === "green") return "g";
  if (f === "yellow") return "a";
  return "r";
};

export function money(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  return (n < 0 ? "-$" : "$") + Math.abs(n).toLocaleString("en-US");
}

// ISO date -> dd/mm/yyyy
export function fdate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  return `${dd}/${mm}/${d.getFullYear()}`;
}

export function roiClass(roi: number | null | undefined): string {
  return (roi ?? 0) < 0 ? "text-red font-bold" : "text-green font-bold";
}

export function roiText(roi: number | null | undefined): string {
  if (roi === null || roi === undefined) return "—";
  return `${roi > 0 ? "+" : ""}${roi}%`;
}
