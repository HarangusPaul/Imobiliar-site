import type { Metadata } from "next";

/**
 * `/dashboard/properties/new`.
 *
 * Creating a listing always produces a draft. Publication is a separate,
 * explicit action guarded by the `properties.publish` capability, so this form
 * has no status field at all.
 */

export const metadata: Metadata = { title: "New property" };

export default function NewPropertyPage() {
  return (
    <div>
      <h1>New property</h1>
      {/* <PropertyForm mode="create" /> from features/properties */}
    </div>
  );
}
