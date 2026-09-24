/**
 * Cross-feature domain types.
 *
 * `types/` holds shapes that more than one feature needs. A type used by
 * exactly one feature belongs inside that feature, next to the API module that
 * produces it.
 */

export interface Account {
  id: string;
  phone_number: string;
  first_name: string;
  last_name: string;
  email: string;
  status: "pending" | "active" | "suspended" | "closed";
  is_phone_verified: boolean;
  roles: string[];
  created_at: string;
}

export interface Entitlements {
  premium_filters: boolean;
  subscriber_only_fields: boolean;
  full_documents: boolean;
  saved_search_alerts: boolean;
}
