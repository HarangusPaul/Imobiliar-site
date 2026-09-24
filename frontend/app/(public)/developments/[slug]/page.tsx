import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { fetchDevelopment } from "@/features/developments/api";
import { isApiError } from "@/lib/api";

/**
 * `/developments/[slug]` - one project with its full structure.
 *
 * The response carries buildings, floors and units in one payload, so the page
 * renders the whole hierarchy without a request waterfall. Which building and
 * floor the visitor is looking at is held in the query string
 * (`?building=...&floor=...`) so the view is linkable.
 */

interface PageProps {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ building?: string; floor?: string }>;
}

async function load(slug: string) {
  try {
    return await fetchDevelopment(slug);
  } catch (error) {
    if (isApiError(error) && error.isNotFound) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const development = await load(slug);
  return { title: development.name, description: development.short_description };
}

export default async function DevelopmentDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const development = await load(slug);

  return (
    <article>
      {/* <BuildingSelector buildings={development.buildings} /> */}
      {/* <FloorPlanViewer /> then <UnitTable /> for the selected floor */}
      {/* <UnitTypeGallery types={development.unit_types} /> */}
      {/* <DevelopmentEnquiryForm developmentSlug={development.slug} /> */}
      <h1>{development.name}</h1>
      <p>{development.available_units} units available</p>
    </article>
  );
}
