import type { Metadata } from "next";

import { AdvisoryCallout } from "@/features/content/components/AdvisoryCallout";
import { homeCallout } from "@/features/content/home";
import { CollectionView } from "@/features/collections/components/CollectionView";
import { collections } from "@/features/collections/data";
import type { SearchParams } from "@/features/collections/query";

/** `/buy` - the for-sale collection. Filters, sort and paging live in the query string. */

const collection = collections.sale;

export const metadata: Metadata = {
  title: collection.title,
  description: collection.introduction,
};

export default async function BuyPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  return (
    <>
      <CollectionView collection={collection} searchParams={await searchParams} />
      <AdvisoryCallout {...homeCallout} />
    </>
  );
}
