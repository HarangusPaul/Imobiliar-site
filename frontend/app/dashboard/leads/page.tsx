import type { Metadata } from "next";

import { fetchDashboardLeads } from "@/features/leads/api";
import { forwardedCookie } from "@/lib/auth/session";

/**
 * `/dashboard/leads` - the inbox.
 *
 * An agent sees leads assigned to them or attached to their own listings;
 * staff see everything. The scoping happens in the backend selector, so this
 * page renders whatever it is given without filtering.
 */

export const metadata: Metadata = { title: "Leads" };

interface PageProps {
  searchParams: Promise<{ status?: string; assigned?: string; page?: string }>;
}

export default async function DashboardLeadsPage({ searchParams }: PageProps) {
  const results = await fetchDashboardLeads(await searchParams, {
    cookie: await forwardedCookie(),
  });

  return (
    <div>
      {/* <LeadTable rows={results.items} /> from features/leads */}
      <p>{results.meta.count ?? 0} leads</p>
    </div>
  );
}
