# Imobiliar - backend

Django modular monolith. Python 3.12+, Django 5, DRF, PostgreSQL.

## Layout

```
backend/
├── config/     composition root: settings, URL zones, service wiring
├── core/       domain-neutral primitives and contracts
├── apps/       business domains
├── services/   replaceable adapters behind core contracts
├── conftest.py shared test fixtures
└── tests/      cross-app tests (boundaries, smoke)
```

The dependency direction is one-way and enforced by `import-linter`
(configured in `pyproject.toml`):

```
core  <-  apps
  ^
services

config composes everything
```

* `core` imports nothing from the project.
* `apps` may import `core`, and must never import `services`.
* `services` may import `core` contracts, and must never import `apps`.
* `config` is the only layer that knows about all three.

Domain apps reach an implementation through
`core.contracts.registry.<contract>_service()`, which resolves a dotted path
from settings at call time. That is what allows the rule above to hold while
`apps/leads` still sends notifications.

See `docs/backend-boundaries.md` for the full rationale and a table of worked
examples.

## Getting started

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows
pip install -e ".[dev]"

cp .env.example .env          # edit DATABASE_URL to point at a local PostgreSQL

python manage.py makemigrations
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser
python manage.py runserver
```

`makemigrations` has not been run in this scaffold - the initial migrations are
generated on first setup, with `accounts.User` in place from the start as
`AUTH_USER_MODEL`.

## Tests

```bash
pytest
lint-imports        # verifies the architectural boundaries
ruff check .
```

## Surfaces

| URL | What it is |
|---|---|
| `/admin/` | Django Admin - the internal CRUD fallback, not the final dashboard |
| `/api/v1/public/` | unauthenticated website data |
| `/api/v1/client/` | authenticated account actions |
| `/api/v1/dashboard/` | agent and staff operations |
| `/api/v1/internal/` | reserved, closed by default |

## Configuration

Everything environment-specific is in `.env` (see `.env.example`). The four
`SERVICE_*` variables select which adapter backs each contract; the defaults
are local, console-based, and depend on no external service.
