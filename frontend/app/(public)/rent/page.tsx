import type { Metadata } from "next";

import { AdvisoryCallout } from "@/features/content/components/AdvisoryCallout";
import { homeCallout } from "@/features/content/home";
import { CollectionView } from "@/features/collections/components/CollectionView";
import { collections } from "@/features/collections/data";
import type { SearchParams } from "@/features/collections/query";

/** `/rent` - the monthly rent collection. Filters, sort and paging live in the query string. */

const collection = collections.rent;

export const metadata: Metadata = {
  title: collection.title,
  description: collection.introduction,
};

export default async function RentPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  return (
    <>
      <CollectionView collection={collection} searchParams={await searchParams} />
      <AdvisoryCallout {...homeCallout} />
    </>
  );
}
