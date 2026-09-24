import type { Metadata } from "next";

/**
 * `/account/saved-properties` - **deferred**.
 *
 * No backend endpoint exists yet. The route is present so the account
 * navigation is complete and the information architecture is settled; it
 * renders an explicit empty state rather than 404.
 */

export const metadata: Metadata = { title: "Saved properties" };

export default function SavedPropertiesPage() {
  return (
    <div>
      <h1>Saved properties</h1>
      <p>Saving listings is coming soon.</p>
    </div>
  );
}
