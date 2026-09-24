import type { Metadata } from "next";

/**
 * `/account/saved-searches` - **deferred**.
 *
 * Will store a filter set and, with the right entitlement, send alerts when
 * new listings match. Neither the endpoint nor the alert workflow exists yet.
 */

export const metadata: Metadata = { title: "Saved searches" };

export default function SavedSearchesPage() {
  return (
    <div>
      <h1>Saved searches</h1>
      <p>Saved searches and alerts are coming soon.</p>
    </div>
  );
}
