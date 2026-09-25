/**
 * The "List a property" questionnaire: its answers, options, per-section
 * completeness and the text an advisor receives.
 *
 * There is no backend endpoint for owner-submitted listings yet. A submission
 * is sent as a lead (kind "valuation") whose message carries every answer, so
 * advisors can review it and create the listing from the dashboard. Photos
 * cannot travel with a lead and stay in the browser; the message says so.
 */

export type ListingType = "sell" | "rent" | "stay";
export type SizeUnit = "sqft" | "m2";

export interface ListingDraft {
  listingType: ListingType;
  propertyType: string;
  categoryLabel: string;
  street: string;
  city: string;
  country: string;
  name: string;
  bedrooms: number;
  bathrooms: number;
  size: string;
  sizeUnit: SizeUnit;
  yearBuilt: string;
  amenities: string[];
  furnished: boolean;
  description: string;
  currency: string;
  price: string;
  availableFrom: string;
  priceOnRequest: boolean;
  contactName: string;
  contactCountry: string;
  contactPhone: string;
}

export const emptyDraft: ListingDraft = {
  listingType: "sell",
  propertyType: "",
  categoryLabel: "",
  street: "",
  city: "",
  country: "",
  name: "",
  bedrooms: 3,
  bathrooms: 2,
  size: "",
  sizeUnit: "m2",
  yearBuilt: "",
  amenities: [],
  furnished: false,
  description: "",
  currency: "EUR",
  price: "",
  availableFrom: "",
  priceOnRequest: false,
  contactName: "",
  contactCountry: "RO",
  contactPhone: "",
};

export const DESCRIPTION_MAX = 1200;
export const DESCRIPTION_MIN = 40;
export const MAX_PHOTOS = 30;

// ---- Options ----------------------------------------------------------------

export const LISTING_TYPES: Array<{ value: ListingType; title: string; description: string }> = [
  { value: "sell", title: "Sell", description: "List it in For Sale" },
  { value: "rent", title: "Rent monthly", description: "Longer stays, furnished or not" },
  { value: "stay", title: "Host stays", description: "Nightly, as a hotel experience" },
];

const opts = (labels: string[]) => labels.map((label) => ({ value: label, label }));

export const PROPERTY_TYPES = opts([
  "Villa",
  "House",
  "Apartment",
  "Penthouse",
  "Townhouse",
  "Lodge",
  "Cabin",
  "Suite",
]);

export const CATEGORY_LABELS = opts(["New", "Exclusive", "Furnished", "Available now"]);

export const COUNTRIES = opts([
  "Romania",
  "Spain",
  "Portugal",
  "France",
  "Italy",
  "Greece",
  "United Kingdom",
  "Germany",
  "Netherlands",
  "Norway",
  "United States",
  "Canada",
  "Mexico",
  "Chile",
  "Japan",
  "Australia",
]);

export const AMENITIES = [
  "Sea view",
  "Pool",
  "Garden",
  "Terrace",
  "Parking",
  "Fireplace",
  "Concierge",
  "Gym",
  "Wine cellar",
  "Elevator",
];

export const CURRENCIES = [
  { value: "EUR", label: "€" },
  { value: "USD", label: "$" },
  { value: "GBP", label: "£" },
  { value: "RON", label: "lei" },
];

/** Wording that depends on what the owner wants to do. */
export function pricingCopy(type: ListingType) {
  return {
    sell: { label: "Asking price", suffix: "total", furnished: "Sold furnished", furnishedDesc: "Furniture and art are included in the price." },
    rent: { label: "Monthly rent", suffix: "/ month", furnished: "Let furnished", furnishedDesc: "Furniture is included in the rent." },
    stay: { label: "Nightly rate", suffix: "/ night", furnished: "Fully furnished", furnishedDesc: "Guests arrive to a ready-to-live home." },
  }[type];
}

// ---- Sections ---------------------------------------------------------------

export type SectionId =
  | "listing-type"
  | "location"
  | "details"
  | "features"
  | "description"
  | "photos"
  | "pricing"
  | "contact";

export interface SectionDef {
  id: SectionId;
  title: string;
  description: string;
  /** Required before submitting. */
  required: boolean;
}

export const SECTIONS: SectionDef[] = [
  { id: "listing-type", title: "Listing type", description: "How will guests or buyers find this property?", required: true },
  { id: "location", title: "Location", description: "We show the neighbourhood publicly, never the exact address.", required: true },
  { id: "details", title: "Property details", description: "The facts people compare first.", required: true },
  { id: "features", title: "Features", description: "Pick everything that applies.", required: false },
  { id: "description", title: "Description", description: "Write it the way you would walk someone through the house.", required: true },
  { id: "photos", title: "Photos", description: "The first photo becomes the cover on every listing card.", required: false },
  { id: "pricing", title: "Pricing & availability", description: "You can change these at any time.", required: true },
  { id: "contact", title: "Contact", description: "Who should our advisors speak to about viewings?", required: true },
];

const filled = (value: string) => value.trim().length > 0;

/** Field-level problems, keyed by field name. Empty when the section is complete. */
export function sectionErrors(
  id: SectionId,
  d: ListingDraft,
  photoCount: number,
): Record<string, string> {
  const e: Record<string, string> = {};
  switch (id) {
    case "listing-type":
      if (!d.propertyType) e.propertyType = "Choose a property type.";
      break;
    case "location":
      if (!filled(d.street)) e.street = "Enter the street address.";
      if (!filled(d.city)) e.city = "Enter the city.";
      if (!d.country) e.country = "Choose a country.";
      break;
    case "details":
      if (!filled(d.name)) e.name = "Give the property a name.";
      if (!(Number(d.size.replace(/[^\d.]/g, "")) > 0)) e.size = "Enter the interior size.";
      if (d.yearBuilt && !/^\d{4}$/.test(d.yearBuilt.trim())) e.yearBuilt = "Use a four-digit year.";
      break;
    case "features":
      if (d.amenities.length === 0) e.amenities = "Pick at least one feature.";
      break;
    case "description":
      if (d.description.trim().length < DESCRIPTION_MIN)
        e.description = `Write at least ${DESCRIPTION_MIN} characters.`;
      break;
    case "photos":
      if (photoCount === 0) e.photos = "Add at least one photo.";
      break;
    case "pricing":
      if (!d.priceOnRequest && !(Number(d.price.replace(/[^\d.]/g, "")) > 0))
        e.price = "Enter a price, or choose price on request.";
      if (!d.availableFrom) e.availableFrom = "Choose a date.";
      break;
    case "contact":
      if (!filled(d.contactName)) e.contactName = "Enter your name.";
      if (d.contactPhone.replace(/\D/g, "").length < 6) e.contactPhone = "Enter a phone number.";
      break;
  }
  return e;
}

// ---- Submission -------------------------------------------------------------

/** Groups digits as the owner types: 3850000 -> 3,850,000. */
export function groupDigits(value: string): string {
  const digits = value.replace(/\D/g, "");
  return digits ? Number(digits).toLocaleString("en-US") : "";
}

export function composeMessage(d: ListingDraft, photoCount: number): string {
  const type = LISTING_TYPES.find((t) => t.value === d.listingType)!;
  const pricing = pricingCopy(d.listingType);
  const currency = CURRENCIES.find((c) => c.value === d.currency)?.label ?? d.currency;
  const unit = d.sizeUnit === "sqft" ? "sq ft" : "m²";

  const lines = [
    `LISTING SUBMISSION — ${type.title}`,
    "",
    `Property: ${d.name} (${d.propertyType}${d.categoryLabel ? `, label: ${d.categoryLabel}` : ""})`,
    `Address: ${d.street}, ${d.city}, ${d.country}`,
    `Details: ${d.bedrooms} bedrooms · ${d.bathrooms} bathrooms · ${d.size} ${unit}${d.yearBuilt ? ` · built ${d.yearBuilt}` : ""}`,
    `Features: ${d.amenities.length ? d.amenities.join(", ") : "none given"}; ${pricing.furnished.toLowerCase()}: ${d.furnished ? "yes" : "no"}`,
    `${pricing.label}: ${d.priceOnRequest ? "price on request" : `${currency} ${d.price} ${pricing.suffix}`}`,
    `Available from: ${d.availableFrom}`,
    `Photos: ${photoCount} selected in the browser (not uploaded — ask the owner to send them)`,
    "",
    "Description:",
    d.description.trim(),
  ];
  return lines.join("\n").slice(0, 4000);
}
