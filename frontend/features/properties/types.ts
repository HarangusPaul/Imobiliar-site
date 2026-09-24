import type { CoverImage, MediaItem } from "@/types/media";
import type { PropertyLocation } from "@/types/location";
import type {
  AvailabilityStatus,
  PropertyType,
  PublicationStatus,
  TransactionType,
} from "@/lib/constants/domain";

/**
 * The card is what a search result returns. It is deliberately small: no
 * description, no gallery, no documents. The backend serializer enforces the
 * same restriction - see `apps/properties/api/serializers/public.py`.
 */
export interface PropertyCard {
  id: string;
  slug: string;
  title: string;
  short_description: string;
  property_type: PropertyType;
  transaction_type: TransactionType;
  availability_status: AvailabilityStatus;
  /** Null when the listing is marked price-on-request. */
  price: string | null;
  currency: string;
  rent_period: string;
  rooms: number | null;
  bathrooms: number | null;
  usable_area: string | null;
  floor: number | null;
  location: PropertyLocation;
  cover_image: CoverImage | null;
  is_featured: boolean;
  published_at: string;
}

/** The detail page. Fetched for exactly one listing at a time. */
export interface PropertyDetail extends PropertyCard {
  description: string;
  total_area: string | null;
  total_floors: number | null;
  year_built: number | null;
  features: Array<{ code: string; name: string; group: string }>;
  gallery: MediaItem[];
  layouts: MediaItem[];
  /** Empty unless the viewer's plan includes document access. */
  documents: MediaItem[];
  /** Null when the exact address is withheld from this viewer. */
  exact_address: string | null;
  created_at: string;
}

/** The dashboard list row - internal state the public API never returns. */
export interface DashboardPropertyRow {
  id: string;
  reference_code: string;
  title: string;
  slug: string;
  property_type: PropertyType;
  transaction_type: TransactionType;
  publication_status: PublicationStatus;
  availability_status: AvailabilityStatus;
  price: string;
  currency: string;
  city: string;
  agent_name: string;
  is_featured: boolean;
  published_at: string | null;
  updated_at: string;
}

export interface PropertyFilters {
  q?: string;
  transaction_type?: TransactionType;
  property_type?: PropertyType[];
  city?: string;
  neighborhood?: string[];
  price_min?: string;
  price_max?: string;
  rooms_min?: string;
  area_min?: string;
  features?: string[];
  sort?: string;
  page?: string;
}
