// Store de filtros del dashboard, compartido entre TopBar, Sidebar y vistas.
import { create } from "zustand";

import type { PropertyFilter } from "@/types/api";

export type FilterKind = "flag" | "county_id" | "auction_type" | "property_type";

interface FilterState {
  flag: string[];
  county_id: string[];
  auction_type: string[];
  property_type: string[];
  min_roi: number | null;
  q: string;
  sort: string;
  page: number;
  page_size: number;
  toggle: (kind: FilterKind, value: string) => void;
  setRoi: (v: number | null) => void;
  setQ: (v: string) => void;
  setSort: (v: string) => void;
  setPage: (p: number) => void;
  clear: () => void;
  applyFilter: (f: PropertyFilter) => void;
  asFilter: () => PropertyFilter;
}

function arr(v?: string[]) {
  return v ? [...v] : [];
}

export const useFilterStore = create<FilterState>((set, get) => ({
  flag: [],
  county_id: [],
  auction_type: [],
  property_type: [],
  min_roi: null,
  q: "",
  sort: "roi_desc",
  page: 1,
  page_size: 20,

  toggle: (kind, value) =>
    set((s) => {
      const cur = s[kind];
      const next = cur.includes(value) ? cur.filter((x) => x !== value) : [...cur, value];
      return { [kind]: next, page: 1 } as Partial<FilterState>;
    }),
  setRoi: (v) => set((s) => ({ min_roi: s.min_roi === v ? null : v, page: 1 })),
  setQ: (v) => set({ q: v, page: 1 }),
  setSort: (v) => set({ sort: v, page: 1 }),
  setPage: (p) => set({ page: p }),
  clear: () =>
    set({
      flag: [],
      county_id: [],
      auction_type: [],
      property_type: [],
      min_roi: null,
      q: "",
      page: 1,
    }),
  applyFilter: (f) =>
    set({
      flag: arr(f.flag),
      county_id: arr(f.county_id),
      auction_type: arr(f.auction_type),
      property_type: arr(f.property_type),
      min_roi: f.min_roi ?? null,
      q: f.q ?? "",
      page: 1,
    }),
  asFilter: () => {
    const s = get();
    const f: PropertyFilter = {};
    if (s.flag.length) f.flag = s.flag;
    if (s.county_id.length) f.county_id = s.county_id;
    if (s.auction_type.length) f.auction_type = s.auction_type;
    if (s.property_type.length) f.property_type = s.property_type;
    if (s.min_roi != null) f.min_roi = s.min_roi;
    if (s.q) f.q = s.q;
    return f;
  },
}));
