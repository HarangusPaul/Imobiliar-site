/** Transport-level shapes. Domain shapes live in `types/` and in each feature. */

export interface ApiMeta {
  count?: number;
  page?: number;
  pages?: number;
  page_size?: number;
  next?: string | null;
  previous?: string | null;
  [key: string]: unknown;
}

export interface ApiEnvelope<T> {
  data: T;
  meta?: ApiMeta;
}

export interface Paginated<T> {
  items: T[];
  meta: ApiMeta;
}
