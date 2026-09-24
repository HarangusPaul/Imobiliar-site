# features/dashboard

Cross-cutting pieces of the internal dashboard that belong to no single domain.

| File | Responsibility |
|---|---|
| `api.ts` | dashboard summary counters |
| `components/DashboardNav.tsx` | sidebar navigation, filtered by role |
| `components/StatCard.tsx` | a single summary tile |
| `components/DataTable.tsx` | column definitions on top of `components/ui/Table` |
| `components/PageHeader.tsx` | title, breadcrumb and primary action |
| `components/EmptyState.tsx` | the dashboard empty-list treatment |
| `components/users/UserTable.tsx` | user administration |
| `components/roles/RoleEditor.tsx` | role and capability assignment |

## What does not belong here

Property management screens live in `features/properties`, the lead inbox in
`features/leads`, plan administration in `features/subscriptions`. This feature
holds the shell and the shared dashboard idioms only. If a component mentions a
domain noun in its name, it belongs to that domain feature.

## Role-aware navigation

`DashboardNav` hides links the account cannot use. That is presentation only:
`middleware.ts` gates the route, and the backend gates the data. Three layers,
and only the last one is authoritative.

## Analytics

`/dashboard/analytics` is a placeholder in this phase. No tracking is
implemented and no analytics product is integrated. When it is built it will
read from domain endpoints backed by domain tables.
