// Tipos TypeScript que reflejan los schemas del backend FastAPI (ClearBid NJ).

export type Flag = "green" | "yellow" | "red";
export type AuctionType = "tax_lien" | "tax_deed" | "sheriff_sale" | "bank_owned";
export type PropertyType = "single_family" | "condo" | "multi_family" | "land";
export type Role = "investor" | "analyst" | "admin";
export type Language = "en" | "es" | "zh" | "de";
export type Theme = "light" | "dark" | "system";
export type Severity = "info" | "warning" | "critical";

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

// --- Auth ---
export interface UserPublic {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: Role;
}
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user?: UserPublic;
}
export interface Challenge {
  challenge_id: string;
  method?: string;
  masked_phone?: string | null;
}
export interface RegisterResponse extends Challenge {
  user_id: string;
}
export interface OAuthResponse {
  status: string;
  challenge_id: string;
  masked_phone?: string | null;
}

// --- Usuario / perfil ---
export interface UserProfile {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  phone_verified: boolean;
  role: Role;
  auth_providers: string[];
  created_at: string;
}
export interface Preferences {
  language: Language;
  theme: Theme;
}

// --- Geografía ---
export interface County {
  id: string;
  name: string;
  state: string;
  main_city?: string | null;
  opportunity_count: number;
}
export interface ZipItem {
  zip: string;
  city: string;
  county_id: string;
  opportunity_count: number;
}

// --- Propiedades ---
export interface PropertyListItem {
  id: string;
  address: string;
  city: string;
  zip: string;
  county_id: string;
  property_type: PropertyType | null;
  flag: Flag | null;
  opening_price: number | null;
  estimated_value: number | null;
  auction_date: string | null;
  thumbnail_url: string | null;
}
export interface FinancialBlock {
  opening_price: number | null;
  total_liens: number | null;
  arv: number | null;
  estimated_repairs: number | null;
  suggested_max_bid: number | null;
  potential_profit: number | null;
  estimated_roi: number | null;
}
export interface LegalBlock {
  auction_type: AuctionType | null;
  auction_date: string | null;
  location: string | null;
  case_number: string | null;
  title_status: string | null;
  occupancy: string | null;
  required_deposit: number | null;
  surviving_irs_lien?: number | null;
  senior_liens?: number | null;
}
export interface PhysicalBlock {
  sqft: number | null;
  lot_sqft: number | null;
  beds: number | null;
  baths: number | null;
  year_built: number | null;
  condition: string | null;
  neighborhood: string | null;
  school_rating: number | null;
  flood_zone: string | null;
  lat: number | null;
  lng: number | null;
}
export interface RuleResult {
  code: string;
  status: "pass" | "fail";
  severity: Severity;
  title: string | null;
  message: string | null;
}
export interface TrafficLight {
  flag: Flag;
  engine_version: string;
  generated_at: string;
  rules: RuleResult[];
}
export interface PropertyDetail {
  id: string;
  address: string;
  city: string;
  zip: string;
  county_id: string;
  property_type: PropertyType | null;
  flag: Flag | null;
  photos: string[];
  financial: FinancialBlock;
  legal: LegalBlock;
  physical: PhysicalBlock;
  traffic_light: TrafficLight | null;
}

// --- Filtro compartido (sección 6.1) ---
export interface PropertyFilter {
  flag?: string[];
  county_id?: string[];
  auction_type?: string[];
  property_type?: string[];
  min_opening?: number;
  max_opening?: number;
  min_roi?: number;
  q?: string;
}

// --- Guardadas ---
export interface SavedItem {
  id: string;
  address: string;
  city: string;
  flag: Flag | null;
  opening_price: number | null;
  saved_at: string;
}

// --- Segmentos ---
export interface Segment {
  id: string;
  name: string;
  filters: PropertyFilter;
  alert_enabled: boolean;
  match_count: number;
  created_at?: string | null;
}

// --- Alertas ---
export interface Alert {
  id: string;
  type: string;
  property_id: string | null;
  title: string;
  body: string | null;
  read: boolean;
  created_at: string;
}
export interface AlertList {
  items: Alert[];
  unread_count: number;
}
export interface AlertSettings {
  new_property: boolean;
  price_drop: boolean;
  auction_reminder: boolean;
  channels: { push: boolean; email: boolean; sms: boolean };
}

// --- Cobertura ---
export interface CoverageItem {
  id: string;
  type: "county" | "zip";
  ref_id: string;
  label: string | null;
}

// --- Facetas ---
export interface Facets {
  total: number;
  flag: Record<string, number>;
  county: { county_id: string; name: string; count: number }[];
  auction_type: Record<string, number>;
  property_type: Record<string, number>;
  roi_buckets: { gte: number; count: number }[];
}

// --- Export ---
export interface ExportJob {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  row_count?: number | null;
  download_url?: string | null;
  expires_at?: string | null;
}

// --- Error estándar ---
export interface ApiError {
  error: { code: string; message: string; details?: { field: string; issue: string }[] };
}
