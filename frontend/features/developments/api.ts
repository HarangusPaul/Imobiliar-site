import { apiGet, apiList, type Paginated, type RequestOptions } from "@/lib/api";

import type { DevelopmentCard, DevelopmentDetail } from "./types";

export function fetchDevelopments(
  params: { city?: string; status?: string; page?: string } = {},
  options: RequestOptions = {},
): Promise<Paginated<DevelopmentCard>> {
  return apiList<DevelopmentCard>("/public/developments/", {
    query: params,
    revalidate: 300,
    tags: ["developments"],
    ...options,
  });
}

/**
 * One project with its entire structure. The backend returns buildings,
 * floors and units in a single bounded query set, so the page needs one
 * request rather than a waterfall per building.
 */
export function fetchDevelopment(
  slug: string,
  options: RequestOptions = {},
): Promise<DevelopmentDetail> {
  return apiGet<DevelopmentDetail>(`/public/developments/${slug}/`, {
    revalidate: 300,
    tags: ["developments", `development:${slug}`],
    ...options,
  });
}
