import type { Metadata } from "next";

import { fetchDevelopments } from "@/features/developments/api";

/** `/developments` - residential projects index. */

export const metadata: Metadata = {
  title: "Developments",
  description: "New residential developments and available apartments.",
};

interface PageProps {
  searchParams: Promise<{ city?: string; status?: string; page?: string }>;
}

export default async function DevelopmentsPage({ searchParams }: PageProps) {
  const results = await fetchDevelopments(await searchParams);

  return (
    <div>
      {/* <DevelopmentCard /> grid from features/developments */}
      <p>{results.meta.count ?? 0} developments</p>
    </div>
  );
}
