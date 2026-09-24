export type MediaCategory =
  | "gallery"
  | "cover"
  | "layout"
  | "floor_plan"
  | "site_plan"
  | "document"
  | "certificate"
  | "video_thumbnail";

export interface MediaItem {
  id: string;
  url: string;
  alt: string;
  title: string;
  category: MediaCategory;
  content_type: string;
}

/** The trimmed shape a listing card receives - one image, no gallery. */
export interface CoverImage {
  url: string;
  alt: string;
}
