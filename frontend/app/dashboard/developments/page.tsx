import type { Metadata } from "next";

/**
 * `/dashboard/developments` - projects, buildings, floors and units.
 *
 * Read and light editing in this phase; Django Admin covers deep structural
 * edits until the dedicated inventory editor is built.
 */

export const metadata: Metadata = { title: "Developments" };

export default function DashboardDevelopmentsPage() {
  return (
    <div>
      <h1>Developments</h1>
      {/* project list, then the building/floor/unit inventory editor */}
    </div>
  );
}
