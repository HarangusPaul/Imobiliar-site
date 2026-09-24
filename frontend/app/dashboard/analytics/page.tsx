import type { Metadata } from "next";

/**
 * `/dashboard/analytics` - **deferred placeholder**.
 *
 * No tracking is implemented and no analytics product is integrated. Domain
 * apps already emit business events through a no-op sink, so the event stream
 * exists in code without going anywhere.
 *
 * When this is built it will read from domain selectors over domain tables -
 * listing performance, lead conversion, response times - which is a different
 * concern from the outbound event contract.
 */

export const metadata: Metadata = { title: "Analytics" };

export default function DashboardAnalyticsPage() {
  return (
    <div>
      <h1>Analytics</h1>
      <p>Reporting is coming soon.</p>
    </div>
  );
}
