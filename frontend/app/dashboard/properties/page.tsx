import type { Metadata } from "next";

import { fetchDashboardProperties } from "@/features/properties/api";
import { forwardedCookie } from "@/lib/auth/session";

/**
 * `/dashboard/properties` - the listing manager.
 *
 * Shows drafts and archived listings, which the public API never returns. The
 * request carries the session cookie explicitly because this runs on the
 * server, and is never cached.
 */

export const metadata: Metadata = { title: "Properties" };

interface PageProps {
  searchParams: Promise<{ status?: string; q?: string; page?: string }>;
}

export default async function DashboardPropertiesPage({ searchParams }: PageProps) {
  const results = await fetchDashboardProperties(await searchParams, {
    cookie: await forwardedCookie(),
  });

  return (
    <div>
      {/* <PageHeader title="Properties" action={<Link href={routes.dashboard.newProperty} />} /> */}
      {/* <DataTable rows={results.items} /> */}
      <p>{results.meta.count ?? 0} listings</p>
    </div>
  );
}
