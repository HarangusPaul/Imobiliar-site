import type { Metadata } from "next";

import { ListingCarousel } from "@/components/shared/ListingCarousel";
import { AdvisoryCallout } from "@/features/content/components/AdvisoryCallout";
import { Hero } from "@/features/content/components/Hero";
import { homeCallout, homeCollections, homeHero } from "@/features/content/home";

/**
 * `/` - the homepage, built from docs/design/homepage.
 *
 * The collections are curated showcase content (see features/content/home.ts)
 * until the backend has listings to feature; this file contains no URL and no
 * fetch.
 */

export const metadata: Metadata = {
  description: "A considered collection of homes to own, rent and experience across the world.",
};

export default function HomePage() {
  return (
    <>
      <Hero {...homeHero} />
      {homeCollections.map((collection) => (
        <ListingCarousel key={collection.index} {...collection} />
      ))}
      <AdvisoryCallout {...homeCallout} />
    </>
  );
}
