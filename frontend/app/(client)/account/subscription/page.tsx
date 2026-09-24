import type { Metadata } from "next";

/**
 * `/account/subscription` - current plan and what it unlocks.
 *
 * Read-only in this phase. There is no checkout: plans are granted
 * administratively from the dashboard.
 */

export const metadata: Metadata = { title: "Subscription" };

export default function SubscriptionPage() {
  return (
    <div>
      <h1>Subscription</h1>
      {/* <SubscriptionStatus /> and <PlanCard /> grid from features/subscriptions */}
    </div>
  );
}
