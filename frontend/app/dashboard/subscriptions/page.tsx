import type { Metadata } from "next";

/**
 * `/dashboard/subscriptions` - plans and user subscriptions.
 *
 * Staff grant, change and cancel subscriptions here. No payment processing is
 * involved anywhere in this phase; a plan price is a label.
 */

export const metadata: Metadata = { title: "Subscriptions" };

export default function DashboardSubscriptionsPage() {
  return (
    <div>
      <h1>Subscriptions</h1>
      {/* plan list, then subscription grants per user */}
    </div>
  );
}
