import type { Metadata } from "next";

import { fetchProperties } from "@/features/properties/api";
import type { PropertyFilters } from "@/features/properties/types";

/**
 * `/properties` - search results.
 *
 * Filter state lives entirely in the query string, which is why this page can
 * be a server component: the first result page renders on the server, is
 * shareable and is indexable. `features/search` owns turning UI controls back
 * into these parameters.
 */

export const metadata: Metadata = {
  title: "Properties",
  description: "Search apartments, houses and commercial spaces.",
};

interface PageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function PropertiesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const results = await fetchProperties(params as PropertyFilters);

  return (
    <div>
      {/* <PropertyFilterPanel /> from features/properties */}
      {/* <ResultsHeader meta={results.meta} /> from features/search */}
      {/* <PropertyGrid items={results.items} /> from features/properties */}
      {/* <Pagination ... /> from components/ui */}
      <p>{results.meta.count ?? 0} results</p>
    </div>
  );
}
