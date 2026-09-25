import type { Route } from "next";

import type { ListingCardData } from "@/components/shared/ListingCard";
import { collectionOrder } from "@/features/collections/data";
import { routes } from "@/lib/constants/routes";

/**
 * Homepage copy, from docs/design/homepage.
 *
 * The carousels show the first listings of each curated collection
 * (features/collections/data.ts), so a listing is written down once. The hero
 * image is a placeholder cropped from the mockup; replace it with the
 * full-resolution original under the same file name.
 */

export const homeHero = {
  eyebrow: "Exceptional places / Distinctive lives",
  title: "Architecture worth living in.",
  description: "A considered collection of homes to own, rent and experience across the world.",
  action: { label: "Explore the collection", href: routes.buy as Route },
  image: { src: "/images/home/hero.jpg", alt: "Concrete residence on a rugged coastline at dusk" },
  caption: "Featured — Casa del Acantilado, Costa Brava",
};

export interface HomeCollection {
  index: string;
  title: string;
  browse: { label: string; href: Route };
  listings: ListingCardData[];
}

const HOME_CAROUSEL_SIZE = 6;

export const homeCollections: HomeCollection[] = collectionOrder.map((collection) => ({
  index: collection.index,
  title: collection.title,
  browse: { label: collection.browseLabel, href: collection.path },
  listings: collection.listings
    .slice(0, HOME_CAROUSEL_SIZE)
    .map(({ id, tag, location, name, facts, rate, image }) => ({
      id,
      href: collection.path,
      tag,
      location,
      name,
      facts,
      rate,
      image,
    })),
}));

export const homeCallout = {
  title: "Looking for somewhere that isn’t listed?",
  text: "Tell us what you have in mind. Our advisors search private and off-market homes on your behalf.",
  action: { label: "Talk to our advisors", href: routes.contact as Route },
};
