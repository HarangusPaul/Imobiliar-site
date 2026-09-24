/**
 * Every property request the app can make.
 *
 * Pages import from here; they never touch `lib/api` directly and never hold a
 * URL string. Moving an endpoint is a change to this file alone.
 */

import { apiGet, apiList, apiPost, type Paginated, type RequestOptions } from "@/lib/api";

import type {
  DashboardPropertyRow,
  PropertyCard,
  PropertyDetail,
  PropertyFilters,
} from "./types";

/** Public search. Cached briefly: listings change, but not within seconds. */
export function fetchProperties(
  filters: PropertyFilters = {},
  options: RequestOptions = {},
): Promise<Paginated<PropertyCard>> {
  return apiList<PropertyCard>("/public/properties/", {
    query: filters as Record<string, string | string[] | undefined>,
    revalidate: 60,
    tags: ["properties"],
    ...options,
  });
}

export function fetchProperty(
  slug: string,
  options: RequestOptions = {},
): Promise<PropertyDetail> {
  return apiGet<PropertyDetail>(`/public/properties/${slug}/`, {
    revalidate: 300,
    tags: ["properties", `property:${slug}`],
    ...options,
  });
}

/** Dashboard list. Never cached - it is scoped to the signed-in user. */
export function fetchDashboardProperties(
  params: { status?: string; q?: string; page?: string } = {},
  options: RequestOptions = {},
): Promise<Paginated<DashboardPropertyRow>> {
  return apiList<DashboardPropertyRow>("/dashboard/properties/", {
    query: params,
    cache: "no-store",
    ...options,
  });
}

export interface CreatePropertyInput {
  title: string;
  property_type: string;
  transaction_type: string;
  address_id: number;
  price: string;
  currency?: string;
  rent_period?: string;
  short_description?: string;
  description?: string;
  rooms?: number | null;
  bathrooms?: number | null;
  usable_area?: string | null;
  total_area?: string | null;
  floor?: number | null;
  year_built?: number | null;
  feature_codes?: string[];
}

export function createProperty(input: CreatePropertyInput): Promise<DashboardPropertyRow> {
  return apiPost<DashboardPropertyRow>("/dashboard/properties/create/", input);
}
