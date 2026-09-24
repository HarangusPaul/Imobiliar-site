import type { Metadata } from "next";

import { fetchDevelopments } from "@/features/developments/api";
import { fetchProperties } from "@/features/properties/api";

/**
 * `/` - the homepage.
 *
 * A server component that fetches featured content at request time with a
 * short revalidation window. Both calls go through feature API modules; this
 * file contains no URL and no fetch.
 */

export const metadata: Metadata = {
  description: "Find apartments, houses and new developments.",
};

export default async function HomePage() {
  const [featured, developments] = await Promise.all([
    fetchProperties({ sort: "newest" }),
    fetchDevelopments(),
  ]);

  return (
    <div>
      {/* <Hero /> from features/content */}
      {/* <SearchBar /> from features/search */}
      {/* <PropertyGrid items={featured.items} /> from features/properties */}
      {/* <DevelopmentRow items={developments.items} /> from features/developments */}
      <p>
        {featured.items.length} featured listings, {developments.items.length} developments.
      </p>
    </div>
  );
}
