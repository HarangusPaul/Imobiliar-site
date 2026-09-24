import type { Metadata } from "next";

/**
 * `/dashboard` - the landing view.
 *
 * Summary tiles scoped to the caller: an agent sees their own portfolio and
 * pipeline, staff see the whole platform. The scoping is done server-side by
 * the selectors, not by hiding tiles here.
 */

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardHomePage() {
  return (
    <div>
      <h1>Dashboard</h1>
      {/* <StatCard /> row: open leads, published listings, drafts */}
    </div>
  );
}
