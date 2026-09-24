export interface PropertyLocation {
  city: string;
  city_slug: string;
  neighborhood: string | null;
  /** What the backend is willing to show publicly. */
  label: string;
}

export interface City {
  slug: string;
  name: string;
  county: string;
  published_count?: number;
}

export interface Neighborhood {
  slug: string;
  name: string;
}
