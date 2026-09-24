# app/api

Next.js route handlers. Kept almost empty on purpose.

This directory is **not** a second backend. Business logic, validation and
persistence belong to Django; putting any of it here would split the domain
across two languages and two deployments.

## What legitimately lives here

- `auth/[...]/route.ts` - thin proxies for actions that must set or clear a
  cookie on this origin, so the session cookie stays first-party.
- `revalidate/route.ts` - a hook the backend can call to invalidate cached
  property or development pages after a publish.
- `health/route.ts` - a local readiness check for the dev server.

## What must never live here

- Direct database access.
- Business rules that duplicate an app service.
- Anything that would let the frontend and backend disagree about a rule.

Ordinary data fetching does not need a route handler at all: server components
call the Django API directly through `lib/api`, and browser requests reach it
through the `/api/backend/*` rewrite in `next.config.ts`.
