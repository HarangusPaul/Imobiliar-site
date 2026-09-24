# features/subscriptions

Plans, the current subscription, and what it unlocks.

| File | Responsibility |
|---|---|
| `api.ts` | available plans; the caller's current subscription |
| `types.ts` | `Plan`, `Subscription`, `Entitlement` shapes |
| `useEntitlements.ts` | hook answering "may this account use X" |
| `components/PlanCard.tsx` | a plan in the comparison grid |
| `components/SubscriptionStatus.tsx` | current plan and validity |
| `components/UpgradePrompt.tsx` | inline nudge shown next to gated features |

## Gating is a hint, not a gate

`useEntitlements` decides whether to render a premium filter as enabled or as
an upgrade prompt. It never decides what data a user receives: the backend
already withholds subscriber-only fields and documents before they leave the
server, so a tampered client gains nothing.

## No payment

There is no checkout, no provider and no billing UI in this phase.
Subscriptions are granted administratively through the dashboard. `PlanCard`
renders a price as a label with no purchase action attached.

## Roles are not plans

Role and subscription are separate axes, exactly as in the backend. An agent on
no plan still has full dashboard access; a client on the top plan is still a
client. Never infer one from the other.
