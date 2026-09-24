import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { fetchProperty } from "@/features/properties/api";
import { isApiError } from "@/lib/api";

/**
 * `/properties/[slug]` - one listing.
 *
 * Addressed by slug, never by database id: slugs are the public identifier and
 * are what the backend detail endpoint accepts.
 */

interface PageProps {
  params: Promise<{ slug: string }>;
}

async function load(slug: string) {
  try {
    return await fetchProperty(slug);
  } catch (error) {
    if (isApiError(error) && error.isNotFound) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const property = await load(slug);
  return {
    title: property.title,
    description: property.short_description,
    openGraph: {
      title: property.title,
      description: property.short_description,
      images: property.cover_image ? [property.cover_image.url] : [],
    },
  };
}

export default async function PropertyDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const property = await load(slug);

  return (
    <article>
      {/* <PropertyGallery images={property.gallery} /> */}
      {/* <PropertyFacts property={property} /> */}
      {/* documents render only when the plan includes them; the array is
          empty otherwise, decided server-side */}
      {/* <PropertyEnquiryForm propertySlug={property.slug} /> from features/leads */}
      <h1>{property.title}</h1>
      <p>{property.location.label}</p>
    </article>
  );
}
