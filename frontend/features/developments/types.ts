import type { CoverImage } from "@/types/media";

/** Mirrors the backend hierarchy: Development > Building > Floor > Unit. */

export interface DevelopmentCard {
  id: string;
  slug: string;
  name: string;
  short_description: string;
  developer_name: string;
  status: "planned" | "under_construction" | "completed" | "sold_out";
  city: string;
  location: string;
  estimated_completion: string | null;
  cover_image: CoverImage | null;
  available_units: number;
  price_from: string | null;
  is_featured: boolean;
}

export interface Unit {
  id: string;
  number: string;
  availability: "available" | "reserved" | "sold" | "rented" | "not_for_sale";
  rooms: number | null;
  usable_area: string | null;
  orientation: string;
  price: string | null;
  currency: string;
  /** Present only when the unit has a live public listing to link to. */
  listing_slug: string | null;
}

export interface Floor {
  id: string;
  level: number;
  name: string;
  unit_count: number;
  floor_plan: string | null;
  units: Unit[];
}

export interface Building {
  id: string;
  name: string;
  code: string;
  status: string;
  floors_above_ground: number;
  floors_below_ground: number;
  estimated_completion: string | null;
  floors: Floor[];
}

export interface UnitType {
  id: string;
  code: string;
  name: string;
  rooms: number;
  bathrooms: number;
  usable_area: string;
  built_area: string | null;
  balcony_area: string | null;
  layout: string | null;
}

export interface DevelopmentDetail extends DevelopmentCard {
  description: string;
  buildings: Building[];
  unit_types: UnitType[];
  availability_summary: Record<string, number>;
}
