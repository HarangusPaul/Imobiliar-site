/**
 * Backend enum values mirrored for the UI.
 *
 * These are labels and orderings, not business rules. Whether a listing may be
 * published is decided by the backend; this file only decides how the word
 * "published" is spelled in the interface.
 */

export const TRANSACTION_TYPES = ["sale", "rent"] as const;
export type TransactionType = (typeof TRANSACTION_TYPES)[number];

export const PROPERTY_TYPES = [
  "apartment",
  "studio",
  "house",
  "villa",
  "land",
  "office",
  "commercial",
  "industrial",
  "garage",
] as const;
export type PropertyType = (typeof PROPERTY_TYPES)[number];

export const PUBLICATION_STATUSES = [
  "draft",
  "pending_review",
  "published",
  "archived",
] as const;
export type PublicationStatus = (typeof PUBLICATION_STATUSES)[number];

export const AVAILABILITY_STATUSES = [
  "available",
  "reserved",
  "sold",
  "rented",
  "unavailable",
] as const;
export type AvailabilityStatus = (typeof AVAILABILITY_STATUSES)[number];

export const LEAD_STATUSES = ["new", "contacted", "qualified", "closed", "spam"] as const;
export type LeadStatus = (typeof LEAD_STATUSES)[number];

export const SORT_OPTIONS = [
  { value: "newest", label: "Newest first" },
  { value: "price_asc", label: "Price: low to high" },
  { value: "price_desc", label: "Price: high to low" },
  { value: "area_desc", label: "Largest first" },
] as const;

export const PROPERTY_TYPE_LABELS: Record<PropertyType, string> = {
  apartment: "Apartment",
  studio: "Studio",
  house: "House",
  villa: "Villa",
  land: "Land",
  office: "Office",
  commercial: "Commercial space",
  industrial: "Industrial space",
  garage: "Garage or parking",
};

export const LEAD_STATUS_LABELS: Record<LeadStatus, string> = {
  new: "New",
  contacted: "Contacted",
  qualified: "Qualified",
  closed: "Closed",
  spam: "Spam",
};
