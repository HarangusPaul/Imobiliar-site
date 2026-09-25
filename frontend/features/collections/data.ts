import { routes } from "@/lib/constants/routes";

import type { ChoiceFilter, Collection, CollectionListing, FilterOption } from "./types";

/**
 * The three curated collections from docs/design (sell, rent, hotel).
 *
 * Static showcase content: the backend has sale and rent listings but no
 * hotel stays, editorial tags or "design-led" flags. When it does, replace the
 * `listings` arrays with API data mapped to `CollectionListing`.
 *
 * Tags are the ones printed in the design, including the "For sale" tags on
 * rentals and stays. The photos are crops of the mockups with those tags baked
 * in, so change a tag only together with its photo.
 */

const img = (slug: string, alt: string) => ({ src: `/images/listings/${slug}.jpg`, alt });

// ---- Shared filter builders -------------------------------------------------

function typeFilter(options: FilterOption[]): ChoiceFilter {
  return {
    kind: "choice",
    param: "type",
    label: "Property type",
    options,
    matches: (listing, value) => listing.type === value,
  };
}

/** Options are "min-max" in USD; either side may be empty. */
function priceFilter(options: FilterOption[]): ChoiceFilter {
  return {
    kind: "choice",
    param: "price",
    label: "Price",
    options,
    matches: (listing, value) => {
      const [min = "", max = ""] = value.split("-");
      return (
        (min === "" || listing.priceUsd >= Number(min)) &&
        (max === "" || listing.priceUsd < Number(max))
      );
    },
  };
}

function atLeastFilter(
  param: string,
  label: string,
  field: "beds" | "sleeps",
  noun: string,
  steps: number[],
): ChoiceFilter {
  return {
    kind: "choice",
    param,
    label,
    options: steps.map((n) => ({ value: String(n), label: `${n}+ ${noun}` })),
    matches: (listing, value) => (listing[field] ?? 0) >= Number(value),
  };
}

const homeChips: FilterOption[] = [
  { value: "house", label: "House" },
  { value: "apartment", label: "Apartment" },
  { value: "design-led", label: "Design-led" },
  { value: "newly-added", label: "Newly added" },
];

// ---- For sale ---------------------------------------------------------------

const saleListings: CollectionListing[] = [
  {
    id: "casa-bruma",
    tag: "For sale",
    location: "Valle de Bravo, Mexico",
    name: "Casa Bruma",
    facts: "4 beds · 5 baths · 5,420 sq ft",
    rate: "$3,850,000",
    image: img("casa-bruma", "Concrete villa in a misty pine forest"),
    type: "house",
    priceUsd: 3_850_000,
    beds: 4,
    features: ["garden", "view"],
    chips: ["house", "design-led"],
  },
  {
    id: "courtyard-house",
    tag: "New",
    location: "Melbourne, Australia",
    name: "The Courtyard House",
    facts: "3 beds · 3 baths · 3,180 sq ft",
    rate: "$2,480,000",
    image: img("courtyard-house", "Brick house around a planted courtyard at dusk"),
    type: "house",
    priceUsd: 2_480_000,
    beds: 3,
    features: ["garden"],
    chips: ["house", "newly-added"],
  },
  {
    id: "aster-ridge",
    tag: "Exclusive",
    location: "Hudson Valley, New York",
    name: "Aster Ridge",
    facts: "5 beds · 4 baths · 18 acres",
    rate: "$4,125,000",
    image: img("aster-ridge", "Black timber house among autumn trees"),
    type: "house",
    priceUsd: 4_125_000,
    beds: 5,
    features: ["land", "view"],
    chips: ["house", "design-led"],
  },
  {
    id: "villa-linea",
    tag: "For sale",
    location: "Mallorca, Spain",
    name: "Villa Linea",
    facts: "6 beds · sea view · pool",
    rate: "€5,900,000",
    image: img("villa-linea", "Clifftop villa with a long pool facing the sea"),
    type: "villa",
    priceUsd: 6_400_000,
    beds: 6,
    features: ["sea-view", "pool"],
    chips: ["design-led"],
  },
  {
    id: "house-on-the-dune",
    tag: "For sale",
    location: "Comporta, Portugal",
    name: "House on the Dune",
    facts: "4 beds · 4 baths · 410 m²",
    rate: "€3,200,000",
    image: img("house-on-the-dune", "Low house among dune grasses with a boardwalk"),
    type: "house",
    priceUsd: 3_470_000,
    beds: 4,
    features: ["sea-view", "pool"],
    chips: ["house", "newly-added"],
  },
  {
    id: "no-17-fitzroy",
    tag: "For sale",
    location: "London, United Kingdom",
    name: "No. 17 Fitzroy",
    facts: "5 beds · 4 baths · 4,800 sq ft",
    rate: "£6,750,000",
    image: img("no-17-fitzroy", "Dark brick building with lit windows on a London square"),
    type: "apartment",
    priceUsd: 8_500_000,
    beds: 5,
    features: ["garden"],
    chips: ["apartment", "newly-added"],
  },
];

// ---- Monthly rent -----------------------------------------------------------

const rentListings: CollectionListing[] = [
  {
    id: "kensington-garden-flat",
    tag: "Available now",
    location: "London, United Kingdom",
    name: "Kensington Garden Flat",
    facts: "3 beds · 2 baths · concierge",
    rate: "£12,500 /mo",
    image: img("kensington-garden-flat", "Living room opening onto a garden"),
    type: "apartment",
    priceUsd: 15_800,
    beds: 3,
    features: ["concierge", "garden"],
    chips: ["apartment"],
  },
  {
    id: "tribeca-loft",
    tag: "Furnished",
    location: "New York, USA",
    name: "Tribeca Loft 5A",
    facts: "2 beds · 2 baths · 2,400 sq ft",
    rate: "$18,000 /mo",
    image: img("tribeca-loft", "Loft with exposed brick and factory windows"),
    type: "apartment",
    priceUsd: 18_000,
    beds: 2,
    features: ["furnished"],
    chips: ["apartment", "design-led"],
  },
  {
    id: "maison-marais",
    tag: "For sale",
    location: "Paris, France",
    name: "Maison Marais",
    facts: "3 beds · terrace · elevator",
    rate: "€9,800 /mo",
    image: img("maison-marais", "Parisian apartment with tall French windows"),
    type: "apartment",
    priceUsd: 10_600,
    beds: 3,
    features: ["terrace"],
    chips: ["apartment"],
  },
  {
    id: "canal-residence",
    tag: "For sale",
    location: "Amsterdam, Netherlands",
    name: "Canal Residence",
    facts: "3 beds · canal view · study",
    rate: "€7,200 /mo",
    image: img("canal-residence", "Beamed living room with windows over a canal"),
    type: "house",
    priceUsd: 7_800,
    beds: 3,
    features: ["view"],
    chips: ["house", "newly-added"],
  },
  {
    id: "pacific-pavilion",
    tag: "For sale",
    location: "Los Angeles, USA",
    name: "Pacific Pavilion",
    facts: "4 beds · pool · canyon view",
    rate: "$24,000 /mo",
    image: img("pacific-pavilion", "Hillside house with a pool above city lights"),
    type: "house",
    priceUsd: 24_000,
    beds: 4,
    features: ["pool", "view"],
    chips: ["house", "design-led"],
  },
  {
    id: "torstrasse-atelier",
    tag: "For sale",
    location: "Berlin, Germany",
    name: "Torstraße Atelier",
    facts: "2 beds · studio · roof terrace",
    rate: "€5,600 /mo",
    image: img("torstrasse-atelier", "Industrial atelier with steel windows"),
    type: "apartment",
    priceUsd: 6_100,
    beds: 2,
    features: ["terrace", "furnished"],
    chips: ["apartment", "design-led", "newly-added"],
  },
];

// ---- Hotel experience -------------------------------------------------------

const stayListings: CollectionListing[] = [
  {
    id: "quarry-house",
    tag: "Editor's pick",
    location: "Paros, Greece",
    name: "The Quarry House",
    facts: "Sleeps 4 · breakfast · sea access",
    rate: "€680 /night",
    image: img("quarry-house", "Carved stone suite opening onto the sea"),
    type: "suite",
    priceUsd: 735,
    sleeps: 4,
    features: ["breakfast", "sea-view"],
    chips: ["beach", "design-led"],
  },
  {
    id: "kiso-forest-lodge",
    tag: "For sale",
    location: "Nagano, Japan",
    name: "Kiso Forest Lodge",
    facts: "Onsen · kaiseki · forest view",
    rate: "¥92,000 /night",
    image: img("kiso-forest-lodge", "Timber lodge in a misty forest"),
    type: "lodge",
    priceUsd: 620,
    sleeps: 2,
    features: ["spa", "breakfast"],
    chips: ["countryside"],
  },
  {
    id: "desert-observatory",
    tag: "For sale",
    location: "Atacama, Chile",
    name: "Desert Observatory",
    facts: "Sleeps 2 · stargazing · transfers",
    rate: "$940 /night",
    image: img("desert-observatory", "Glowing desert lodge under the Milky Way"),
    type: "lodge",
    priceUsd: 940,
    sleeps: 2,
    features: ["transfers"],
    chips: ["countryside", "design-led"],
  },
  {
    id: "fogo-island-studio",
    tag: "For sale",
    location: "Newfoundland, Canada",
    name: "Fogo Island Studio",
    facts: "Ocean view · sauna · breakfast",
    rate: "$760 /night",
    image: img("fogo-island-studio", "Black studio on rocks above a stormy sea"),
    type: "cabin",
    priceUsd: 760,
    sleeps: 2,
    features: ["sea-view", "spa", "breakfast"],
    chips: ["beach", "design-led", "newly-added"],
  },
  {
    id: "masseria-nera",
    tag: "For sale",
    location: "Puglia, Italy",
    name: "Masseria Nera",
    facts: "Pool · local dining · bikes",
    rate: "€590 /night",
    image: img("masseria-nera", "Whitewashed masseria among olive trees"),
    type: "villa",
    priceUsd: 640,
    sleeps: 6,
    features: ["pool", "breakfast"],
    chips: ["countryside"],
  },
  {
    id: "cabin-08",
    tag: "For sale",
    location: "Lofoten, Norway",
    name: "Cabin 08",
    facts: "Sleeps 4 · sauna · fjord view",
    rate: "NOK 7,900 /night",
    image: img("cabin-08", "Black cabin on snow below jagged mountains"),
    type: "cabin",
    priceUsd: 740,
    sleeps: 4,
    features: ["spa", "sea-view"],
    chips: ["design-led", "newly-added"],
  },
];

// ---- Collections ------------------------------------------------------------

export const collections: Record<"sale" | "rent" | "stay", Collection> = {
  sale: {
    key: "sale",
    path: routes.buy,
    eyebrow: "Own the exceptional",
    title: "For Sale",
    introduction: "Architectural homes selected for enduring value.",
    index: "01 / Collection",
    browseLabel: "Explore all for sale",
    filters: [
      typeFilter([
        { value: "house", label: "House" },
        { value: "villa", label: "Villa" },
        { value: "apartment", label: "Apartment" },
      ]),
      priceFilter([
        { value: "-3000000", label: "Under $3M" },
        { value: "3000000-5000000", label: "$3M – $5M" },
        { value: "5000000-", label: "Over $5M" },
      ]),
      atLeastFilter("beds", "Beds & baths", "beds", "beds", [2, 3, 4, 5]),
      {
        kind: "features",
        param: "feature",
        label: "More filters",
        options: [
          { value: "sea-view", label: "Sea view" },
          { value: "pool", label: "Pool" },
          { value: "garden", label: "Garden" },
          { value: "land", label: "Land" },
        ],
      },
    ],
    chips: homeChips,
    listings: saleListings,
  },
  rent: {
    key: "rent",
    path: routes.rent,
    eyebrow: "Live beautifully, now",
    title: "Monthly Rent",
    introduction: "Flexible residences without compromise.",
    index: "02 / Collection",
    browseLabel: "Explore all monthly rent",
    filters: [
      typeFilter([
        { value: "house", label: "House" },
        { value: "apartment", label: "Apartment" },
      ]),
      priceFilter([
        { value: "-10000", label: "Under $10k /mo" },
        { value: "10000-20000", label: "$10k – $20k /mo" },
        { value: "20000-", label: "Over $20k /mo" },
      ]),
      atLeastFilter("beds", "Beds & baths", "beds", "beds", [2, 3, 4]),
      {
        kind: "features",
        param: "feature",
        label: "More filters",
        options: [
          { value: "furnished", label: "Furnished" },
          { value: "terrace", label: "Terrace" },
          { value: "pool", label: "Pool" },
          { value: "concierge", label: "Concierge" },
        ],
      },
    ],
    chips: homeChips,
    listings: rentListings,
  },
  stay: {
    key: "stay",
    path: routes.stay,
    eyebrow: "Stay somewhere unforgettable",
    title: "Hotel Experience",
    introduction: "Design-led escapes, from one night onward.",
    index: "03 / Collection",
    browseLabel: "Explore all hotel experience",
    filters: [
      typeFilter([
        { value: "suite", label: "Suite" },
        { value: "lodge", label: "Lodge" },
        { value: "cabin", label: "Cabin" },
        { value: "villa", label: "Villa" },
      ]),
      atLeastFilter("guests", "Guests", "sleeps", "guests", [2, 4, 6]),
      { kind: "dates", label: "Dates" },
      {
        kind: "features",
        param: "feature",
        label: "More filters",
        options: [
          { value: "breakfast", label: "Breakfast" },
          { value: "spa", label: "Sauna or spa" },
          { value: "sea-view", label: "Sea view" },
          { value: "pool", label: "Pool" },
        ],
      },
    ],
    chips: [
      { value: "beach", label: "Beach" },
      { value: "countryside", label: "Countryside" },
      { value: "design-led", label: "Design-led" },
      { value: "newly-added", label: "Newly added" },
    ],
    listings: stayListings,
  },
};

export const collectionOrder = [collections.sale, collections.rent, collections.stay];
