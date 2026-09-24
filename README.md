# Imobiliar

Real-estate platform: a public property website and an internal dashboard.

```
Django + DRF + PostgreSQL   ·   Next.js + React + TypeScript
```

## Structure

```
backend/     Django modular monolith (config / core / apps / services)
frontend/    Next.js App Router application
docs/        architecture documentation
```

## Start here

| Document | What it covers |
|---|---|
| [docs/architecture.md](docs/architecture.md) | the decisions, the repository tree, deferred features, implementation order |
| [docs/backend-boundaries.md](docs/backend-boundaries.md) | `core` vs `apps` vs `services` vs `config`, with worked examples |
| [docs/domain-model.md](docs/domain-model.md) | entities, relationships, and why they are shaped that way |
| [docs/api-conventions.md](docs/api-conventions.md) | API zones, envelopes, errors, pagination, endpoint list |
| [docs/frontend-architecture.md](docs/frontend-architecture.md) | route groups, feature modules, state, pages |

Setup instructions are in [backend/README.md](backend/README.md) and
[frontend/README.md](frontend/README.md).

## The one rule

```
core  <-  apps
  ^
services

config composes everything
```

`core` knows nothing about real estate. `apps` own the domains and never import
a provider. `services` are replaceable adapters and never contain business
rules. `config` is the only layer that knows all three.

Enforced by `lint-imports` and by `backend/tests/test_architecture_boundaries.py`.
