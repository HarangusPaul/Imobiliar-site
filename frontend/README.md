# Imobiliar - frontend

Next.js (App Router) + React + TypeScript.

## Layer responsibilities

| Layer | Owns | Must not contain |
|---|---|---|
| `app/` | routing, layouts, server-side data loading, metadata | business logic, reusable components, fetch calls |
| `features/` | one business domain each: API module, types, domain components, forms | generic UI primitives, another domain's concerns |
| `components/` | `ui/` generic primitives, `layout/` shells, `shared/` cross-feature pieces | domain knowledge in `ui/`, feature-specific code |
| `lib/` | the HTTP client, auth helpers, validation primitives, constants | domain models, components |
| `types/` | shapes used by more than one feature | shapes used by exactly one feature |

### app/

Route definitions and nothing else. A page is thin: it resolves parameters,
calls one or two feature API functions, and composes feature components. If a
page file grows logic, that logic belongs to a feature.

Four route groups, because they have genuinely different chrome:

- `(public)` - the marketing and browsing site, header and footer
- `(auth)` - login and register, centred card, no navigation
- `(client)` - the signed-in account area, account sidebar
- `dashboard` - the internal tool (a real segment, not a group, since
  `/dashboard` is a real prefix)

### features/

The unit of ownership. Each feature holds `api.ts`, `types.ts`, optionally
`schema.ts`, and its own `components/`. A feature may import from `lib`,
`components` and `types`. Cross-feature imports are a smell: if two features
need the same thing, it moves to `components/shared` or `types/`.

### components/

`ui/` must be reusable in a project that is not about real estate.
`layout/` holds the four shells. `shared/` is for pieces with some domain
awareness used by two or more features.

### lib/

`lib/api` is the only place that calls `fetch`. `lib/auth` reads the session.
`lib/validation` holds reusable schema primitives. `lib/constants` holds routes
and mirrored backend enums.

## Data flow

```
page (server component)
  -> features/<domain>/api.ts
    -> lib/api/client.ts
      -> /api/backend/*  (browser)  or  BACKEND_ORIGIN/api/v1/*  (server)
```

No component calls `fetch`. No page holds a URL string. Changing an endpoint is
an edit to one feature's `api.ts`.

## State

| State | Where it lives |
|---|---|
| Search filters, pagination, selected building/floor | the URL query string |
| Server data | server components, with Next.js fetch caching |
| Form input | local component state |
| Session / account | fetched in the layout, passed down as props |

There is no global client store, and none is needed: the state that would go in
one is either in the URL (and therefore shareable) or on the server.

## Authentication

A Django session cookie. The browser holds no token. Browser requests go to
`/api/backend/*` on this origin and are rewritten to the API, which keeps the
cookie first-party and removes CORS from the picture entirely.

`middleware.ts` checks cookie presence only. Layouts fetch the account and
redirect on role. The backend re-checks everything and is the only authority.

## Getting started

```bash
npm install
cp .env.example .env.local
npm run dev
```

The Django API must be running on `BACKEND_ORIGIN` (default
`http://localhost:8000`).
