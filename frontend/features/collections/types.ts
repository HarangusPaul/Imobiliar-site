import type { Route } from "next";

import type { ListingCardData } from "@/components/shared/ListingCard";

export type CollectionKey = "sale" | "rent" | "stay";

/** A curated listing: the card's display strings plus the fields filters read. */
export interface CollectionListing extends Omit<ListingCardData, "href"> {
  /** Property type option value, e.g. "house". */
  type: string;
  /** Approximate price in USD, used only for price filtering and sorting. */
  priceUsd: number;
  beds?: number;
  sleeps?: number;
  /** "More filters" feature codes, e.g. "pool". */
  features: string[];
  /** Quick-filter chip codes, e.g. "design-led". */
  chips: string[];
}

export interface FilterOption {
  value: string;
  label: string;
}

/** A single-choice dropdown in the search bar. */
export interface ChoiceFilter {
  kind: "choice";
  param: string;
  label: string;
  options: FilterOption[];
  matches: (listing: CollectionListing, value: string) => boolean;
}

/** A multi-choice dropdown: every checked feature must be present. */
export interface FeatureFilter {
  kind: "features";
  param: string;
  label: string;
  options: FilterOption[];
}

/** Check-in / check-out. Kept in the URL; there is no availability data yet. */
export interface DatesFilter {
  kind: "dates";
  label: string;
}

export type SearchFilter = ChoiceFilter | FeatureFilter | DatesFilter;

export interface Collection {
  key: CollectionKey;
  path: Route;
  eyebrow: string;
  title: string;
  introduction: string;
  /** Homepage carousel copy. */
  index: string;
  browseLabel: string;
  filters: SearchFilter[];
  chips: FilterOption[];
  listings: CollectionListing[];
}
