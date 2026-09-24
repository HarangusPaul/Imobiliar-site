# Architecture

## Decisions

1. **Django modular monolith, not microservices.** One database, one
   deployment, hard internal boundaries. At 5,000+ properties the scaling
   pressure is on queries and indexes, not on process isolation. Boundaries are
   enforced in code (`import-linter` plus a test), so the option to split later
   stays open without paying the distributed-systems cost now.

2. **Four layers with a one-way dependency graph.** `core` knows nothing about
   the project. `apps` own business domains and may use `core`. `services` are
   replaceable adapters behind `core` contracts. `config` composes everything.

3. **Contracts, not vendors.** Domain apps never import an implementation. They
   ask `core.contracts.registry` for a capability, which resolves a dotted path
   from settings at call time. Adding a real channel later is a settings change
   plus one new file under `services/`.

4. **The API zone is part of the contract.** `/public/`, `/client/`,
   `/dashboard/` and `/internal/` are separate URL trees with separate
   serializers and permissions. The same resource exposed to two audiences is
   two endpoints, never one endpoint that reshapes itself based on who is
   asking.

5. **Thin views, services for writes, selectors for reads.** A view validates
   input and calls one function. Every write workflow is a service; every
   non-trivial query is a selector. This is what keeps query shape and
   transaction boundaries reviewable as the project grows.

6. **Phone number as identity, from the first migration.** A custom user model
   with `AUTH_USER_MODEL = "accounts.User"` and no username field. Verification
   state is modelled now with no delivery channel configured, so OTP is a
   services change rather than an account-architecture change.

7. **Roles and entitlements are data, not code.** A role is a row with
   capabilities; a plan is a row with entitlements. Adding either is
   administrative. Code asks `has_capability(user, ...)` or
   `has_entitlement(user, ...)`, never `if user.role == "agent"`.

8. **Lightweight public cards.** Listing results never carry descriptions,
   galleries, documents or layouts. The card queryset, the card serializer and
   the frontend `PropertyCard` type all enforce the same restriction.

9. **Unit and Property are separate.** Inventory (`developments.Unit`) and
   listing (`properties.Property`) have different lifecycles and are joined by
   an optional one-to-one. See `domain-model.md`.

10. **Bytes never touch PostgreSQL.** `apps/media` stores metadata and an
    opaque storage key; `services/storage` owns the file.

11. **Django Admin is a fallback, not the product.** Registered thoroughly and
    usable from day one, with destructive operations routed through domain
    services so even the admin cannot skip a rule. The dashboard will be React.

12. **Frontend state lives in the URL.** Filters, pagination and the selected
    building/floor are query parameters. No global client store.

## Repository

```
Imobiliar-site/
├── backend/
│   ├── config/          composition root
│   ├── core/            domain-neutral primitives and contracts
│   ├── apps/            business domains
│   ├── services/        replaceable adapters
│   ├── tests/           cross-cutting tests
│   ├── conftest.py
│   ├── manage.py
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── app/             routes and layouts
│   ├── features/        one folder per business domain
│   ├── components/      ui / layout / shared
│   ├── lib/             api, auth, validation, constants
│   ├── types/           cross-feature shapes
│   ├── middleware.ts
│   ├── package.json
│   └── README.md
│
└── docs/
    ├── architecture.md
    ├── backend-boundaries.md
    ├── frontend-architecture.md
    ├── domain-model.md
    └── api-conventions.md
```

## Deferred

Explicitly out of scope for this phase, and why the current design already
accommodates each one.

| Deferred | Where it plugs in |
|---|---|
| OTP delivery (SMS / WhatsApp) | a new `services/verification/` module; `apps/accounts` unchanged |
| Real notification transport | a new `services/notifications/` module |
| Non-local file storage | a new `services/storage/` module |
| Analytics collection | a new `services/analytics/` module |
| Payments and billing | a caller of `apps/subscriptions.services.lifecycle`, not a rewrite of it |
| Saved properties, saved searches, alerts | new models and endpoints in `apps/accounts` or a sibling app; routes already exist in the frontend |
| Map and geographic search | `locations` already stores coordinates; PostGIS becomes additive |
| Dashboard analytics screens | domain selectors over domain tables; route already present |
| Full CMS | `apps/content` stays minimal until there is a real requirement |
| Property comparison, valuation tools, multi-language | not modelled; no current design blocks them |
| A background job broker | `core.tasks.Task.enqueue` already defers work to after-commit; only the base class changes |

## Suggested implementation order

1. **Foundation.** Create the PostgreSQL database, install dependencies, run
   `makemigrations` for all apps with `accounts.User` in place, migrate, and run
   `seed_roles`. Confirm `pytest` and `lint-imports` pass.
2. **Identity.** Registration, login and logout end to end, plus the `(auth)`
   route group. This unblocks every authenticated surface.
3. **Geography and taxonomy.** Seed countries, cities, neighborhoods and the
   feature list. Small, and everything else references it.
4. **Listings.** Property model, validators, services and Django Admin. Create
   real listings through the admin before building any UI.
5. **Public listing surface.** The public search and detail endpoints, then
   `/properties` and `/properties/[slug]`. First externally visible milestone.
6. **Media.** Upload through the storage contract, galleries, cover images, and
   layout files - listings look real only once they have photographs.
7. **Leads.** The public contact and enquiry forms, intake, auto-assignment and
   the notification call. This is the first revenue-relevant loop.
8. **Developments.** The full hierarchy, admin inventory management, then the
   public project pages.
9. **Dashboard.** Shell, property manager, lead inbox. Replaces admin for daily
   work; admin stays as the fallback.
10. **Subscriptions.** Plans, entitlements and gated filters and fields, once
    there is enough data for gating to mean anything.
11. **Account area.** Profile and request history, then saved properties and
    saved searches when their endpoints exist.
12. **Hardening.** Query budgets on the list endpoints, index verification
    against real volume, audit coverage review.

Steps 1-5 form the first useful release: a public property site with an
internal admin behind it.
