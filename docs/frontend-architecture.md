# Frontend architecture

Next.js App Router, React, TypeScript.

## Layer responsibilities

| Layer | Owns | Must not contain |
|---|---|---|
| `app/` | routing, layouts, server-side loading, metadata | business logic, reusable components, `fetch` |
| `features/` | one business domain each | generic primitives, another domain's concerns |
| `components/` | `ui/`, `layout/`, `shared/` | domain knowledge in `ui/` |
| `lib/` | HTTP client, auth, validation primitives, constants | domain models, components |
| `types/` | shapes used by more than one feature | single-feature shapes |

### app/

Routes and nothing else. A page resolves its parameters, calls one or two
feature API functions, and composes feature components. If a page grows logic,
the logic belongs to a feature.

Route groups exist because the four surfaces have genuinely different chrome:

| Group | URLs | Shell |
|---|---|---|
| `(public)` | `/`, `/properties`, `/developments`, `/contact`, `/about` | header + footer |
| `(auth)` | `/login`, `/register` | centred card, no navigation |
| `(client)` | `/account/*` | header + account sidebar |
| `dashboard` | `/dashboard/*` | dashboard sidebar + top bar |

`dashboard` is a plain segment rather than a group because `/dashboard` is a
real URL prefix.

The root layout holds `<html>` and `<body>` only. It renders no header, because
each group mounts its own shell and a site header there would have to be undone
by the dashboard and the login page.

`app/api/` is **not** a second backend. See `app/api/README.md`.

### features/

The unit of ownership. Each holds `api.ts`, `types.ts`, optionally `schema.ts`,
and its own `components/`.

| Feature | Owns |
|---|---|
| `properties` | listing API calls, property types, cards, grid, gallery, filter panel, dashboard form |
| `developments` | project API, the building/floor/unit hierarchy UI, unit tables, layouts |
| `search` | URL-state mechanics, search bar, filter chips, sort control |
| `leads` | contact and enquiry forms, schemas, inbox table, lead timeline |
| `auth` | login, register, logout, session forms |
| `account` | profile, request history, saved items (deferred) |
| `subscriptions` | plans, current subscription, entitlement hook, upgrade prompts |
| `dashboard` | shell navigation, stat cards, data table, user and role admin |
| `content` | presentation pages, SEO metadata builder, hero |

A feature may import `lib`, `components` and `types`. Cross-feature imports are
a smell: if two features need the same thing, it moves to `components/shared`
or `types/`.

### components/

`ui/` - `Button`, `Input`, `Select`, `Modal`, `Table`, `Pagination`, `Badge`,
`Card`, and the rest. The rule: a component here must be reusable in a project
that is not about real estate. `Badge` takes `variant="success"`, never
`status="published"`. If it needs a domain type in order to compile, it is in
the wrong folder.

`layout/` - `Header`, `Footer`, `Sidebar`, `PublicShell`, `AuthShell`,
`AccountShell`, `DashboardShell`. Server components that receive the account as
a prop from the layout that fetched it.

`shared/` - `Price`, `AreaValue`, `PhoneLink`, `MediaImage`, `ConfirmDialog`.
Two or more features use it, and it carries some domain awareness. `Price`
knows that a rental shows a period suffix, which disqualifies it from `ui/`,
but three features need it.

### lib/

`lib/api` is the **only** place that calls `fetch`. `client.ts` builds URLs and
handles the envelope; `errors.ts` turns the backend error shape into `ApiError`
with `fieldErrors()` for forms.

`lib/auth` reads the session and exposes role helpers, for rendering and never
for security. `lib/validation` holds reusable schema primitives; form-specific
schemas live in their feature. `lib/constants` holds route builders and
mirrored backend enums (labels and ordering, not rules).

### types/

Shapes used by more than one feature: `Account`, `PropertyLocation`,
`MediaItem`. A type used by exactly one feature lives in that feature, next to
the API module that produces it.

## Data flow

```
page (server component)
  -> features/<domain>/api.ts
    -> lib/api/client.ts
      -> /api/backend/*  (browser)  or  BACKEND_ORIGIN/api/v1/*  (server)
```

No component calls `fetch`. No page holds a URL string. Moving an endpoint is
an edit to one feature `api.ts`.

Caching follows who the data belongs to: public reads revalidate on a timer and
carry tags (`properties`, `property:<slug>`); anything user-scoped is
`no-store`, because a stale dashboard is a correctness bug.

## State

| State | Where it lives | Why |
|---|---|---|
| Search filters, pagination, selected building/floor | the URL query string | shareable, bookmarkable, indexable, and lets the server render page one |
| Server data | server components + Next.js fetch cache | no client refetch for the initial render |
| Form input | local component state | nothing else needs it |
| Session / account | fetched in the layout, passed as props | one lookup per navigation |

There is no global client store and none is needed: the state that would go in
one is either in the URL or on the server.

## Authentication

A Django session cookie. The browser holds no token. Requests go to
`/api/backend/*` on this origin and are rewritten to the API, keeping the
cookie first-party and removing CORS entirely.

Three layers of access control, only one of which is authoritative:

1. `middleware.ts` - cookie presence. Redirects anonymous visitors so they do
   not render a shell that will fail every call.
2. Layouts - fetch the account and redirect on role. `DashboardLayout` sends a
   client account back to `/account`.
3. **The backend** - `apps/access` and `apps/subscriptions` re-check every
   request. A forced-open dashboard renders empty and erroring.

Hiding navigation is presentation, never protection.

## Pages

### Public

| Route | Content |
|---|---|
| `/` | hero, search bar, featured listings, developments |
| `/properties` | filter panel, results grid, pagination; all state in the URL |
| `/properties/[slug]` | gallery, facts, features, layouts, documents (gated), enquiry form, similar listings |
| `/developments` | project cards with available-unit counts and price-from |
| `/developments/[slug]` | building selector, floor plan, unit table, unit types, enquiry form |
| `/contact` | general contact form |
| `/about` | presentation page from `apps/content` |

### Auth

| Route | Content |
|---|---|
| `/login` | phone + password; `?next=` carries the intended destination |
| `/register` | account creation; a verification step joins this flow later without a route change |

### Client account

| Route | Content |
|---|---|
| `/account` | overview |
| `/account/profile` | name, email, preferences; phone readonly |
| `/account/saved-properties` | **deferred** - explicit empty state |
| `/account/saved-searches` | **deferred** - explicit empty state |
| `/account/requests` | the client's own enquiries and their status |
| `/account/subscription` | current plan and entitlements; no checkout |

### Dashboard

| Route | Content |
|---|---|
| `/dashboard` | summary tiles, scoped server-side |
| `/dashboard/properties` | listing manager including drafts and archived |
| `/dashboard/properties/new` | create; always produces a draft |
| `/dashboard/properties/[id]` | edit by UUID; details, media, publication, leads, history |
| `/dashboard/developments` | projects and inventory |
| `/dashboard/leads` | inbox, scoped by capability, with status counts |
| `/dashboard/leads/[id]` | message, subject, timeline, assignment |
| `/dashboard/users` | requires `users.manage` |
| `/dashboard/roles` | roles as data; new roles without a deployment |
| `/dashboard/subscriptions` | grant and cancel; no payment |
| `/dashboard/analytics` | **deferred placeholder** |

## Deferred on the frontend

Saved properties, saved searches and alerts; the OTP verification screen;
dashboard analytics; a full media upload editor; map search. Each has a route
or a component slot reserved, so adding it later means filling in a module
rather than reworking the structure.
