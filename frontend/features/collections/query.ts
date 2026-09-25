import type { Route } from "next";

import type { Collection, CollectionListing } from "./types";

/**
 * Collection search state lives in the query string, so a filtered page is
 * shareable and renders on the server. This module turns the query into
 * results and builds links that change one part of it.
 */

export const PAGE_SIZE = 6;

export const SORTS = [
  { value: "featured", label: "Featured" },
  { value: "price-asc", label: "Price: low to high" },
  { value: "price-desc", label: "Price: high to low" },
] as const;

export type SortValue = (typeof SORTS)[number]["value"];

export type SearchParams = Record<string, string | string[] | undefined>;

export interface CollectionQuery {
  q: string;
  /** Single-choice dropdowns, keyed by their param. */
  choices: Record<string, string>;
  features: string[];
  chip: string;
  sort: SortValue;
  page: number;
  checkIn: string;
  checkOut: string;
}

const first = (value: string | string[] | undefined) =>
  (Array.isArray(value) ? value[0] : value)?.trim() ?? "";

const all = (value: string | string[] | undefined) =>
  (Array.isArray(value) ? value : value ? [value] : []).filter(Boolean);

export function parseQuery(collection: Collection, params: SearchParams): CollectionQuery {
  const choices: Record<string, string> = {};
  for (const filter of collection.filters) {
    if (filter.kind !== "choice") continue;
    const value = first(params[filter.param]);
    if (filter.options.some((option) => option.value === value)) choices[filter.param] = value;
  }

  const featureValues = new Set(
    collection.filters.flatMap((f) => (f.kind === "features" ? f.options : [])).map((o) => o.value),
  );
  const chip = first(params.chip);
  const sort = first(params.sort);
  const page = Number.parseInt(first(params.page), 10);

  return {
    q: first(params.q).slice(0, 120),
    choices,
    features: all(params.feature).filter((value) => featureValues.has(value)),
    chip: collection.chips.some((c) => c.value === chip) ? chip : "",
    sort: SORTS.some((s) => s.value === sort) ? (sort as SortValue) : "featured",
    page: Number.isFinite(page) && page > 1 ? Math.min(page, 50) : 1,
    checkIn: first(params.checkin),
    checkOut: first(params.checkout),
  };
}

export function filterListings(collection: Collection, query: CollectionQuery): CollectionListing[] {
  const needle = query.q.toLowerCase();

  const results = collection.listings.filter((listing) => {
    if (needle && !`${listing.name} ${listing.location}`.toLowerCase().includes(needle)) {
      return false;
    }
    if (query.chip && !listing.chips.includes(query.chip)) return false;
    if (!query.features.every((feature) => listing.features.includes(feature))) return false;
    return collection.filters.every(
      (filter) =>
        filter.kind !== "choice" ||
        !query.choices[filter.param] ||
        filter.matches(listing, query.choices[filter.param]!),
    );
  });

  if (query.sort === "price-asc") results.sort((a, b) => a.priceUsd - b.priceUsd);
  if (query.sort === "price-desc") results.sort((a, b) => b.priceUsd - a.priceUsd);
  return results;
}

export function isFiltered(query: CollectionQuery): boolean {
  return Boolean(
    query.q ||
      query.chip ||
      query.features.length ||
      Object.keys(query.choices).length ||
      query.checkIn ||
      query.checkOut,
  );
}

/** Serialises a query back into a link, dropping defaults. */
export function queryHref(
  path: string,
  query: CollectionQuery,
  changes: Partial<CollectionQuery> = {},
): Route {
  const next = { ...query, ...changes };
  const params = new URLSearchParams();
  if (next.q) params.set("q", next.q);
  for (const [param, value] of Object.entries(next.choices)) params.set(param, value);
  for (const feature of next.features) params.append("feature", feature);
  if (next.checkIn) params.set("checkin", next.checkIn);
  if (next.checkOut) params.set("checkout", next.checkOut);
  if (next.chip) params.set("chip", next.chip);
  if (next.sort !== "featured") params.set("sort", next.sort);
  if (next.page > 1) params.set("page", String(next.page));
  const search = params.toString();
  return (search ? `${path}?${search}` : path) as Route;
}
