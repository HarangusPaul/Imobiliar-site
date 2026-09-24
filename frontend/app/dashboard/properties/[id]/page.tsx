import type { Metadata } from "next";

/**
 * `/dashboard/properties/[id]` - edit one listing.
 *
 * Addressed by UUID rather than slug: the dashboard needs to reach drafts and
 * archived listings, whose slugs may be absent or may change, and internal
 * routes have no SEO reason to be readable.
 *
 * Tabs: details, media, publication, leads, history.
 */

export const metadata: Metadata = { title: "Edit property" };

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function EditPropertyPage({ params }: PageProps) {
  const { id } = await params;

  return (
    <div>
      <h1>Edit property</h1>
      <p>{id}</p>
      {/* <PropertyForm mode="edit" /> and the media manager */}
    </div>
  );
}
