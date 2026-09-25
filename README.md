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

## How to run

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- PostgreSQL running locally

### Quick start (Windows)

After creating the database (step 1 below), run from the repository root:

```powershell
.\run.cmd            # or: .\run.ps1
.\run.cmd -Setup     # force reinstall of Python and npm dependencies
```

On first run it creates the venv, installs dependencies, copies the `.env`
examples, runs migrations and `seed_roles`. It then starts Django on :8000 in a
new window and Next.js on :3000 in the current one. It does not create an admin
user, so run `python manage.py createsuperuser` in `backend/` once yourself.

The steps below do the same thing by hand.

### 1. Database

Create the database and user that `backend/.env.example` expects:

```sql
CREATE USER imobiliar WITH PASSWORD 'imobiliar' CREATEDB;
CREATE DATABASE imobiliar OWNER imobiliar;
```

### 2. Backend (Django API on http://localhost:8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux / Git Bash
pip install -e ".[dev]"

cp .env.example .env              # adjust DATABASE_URL if needed

python manage.py makemigrations
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser
python manage.py runserver
```

Django Admin is at http://localhost:8000/admin/, the API at
http://localhost:8000/api/v1/.

### 3. Frontend (Next.js on http://localhost:3000)

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local        # BACKEND_ORIGIN defaults to http://localhost:8000
npm run dev
```

Open http://localhost:3000. The backend must be running for pages that load data.

### Tests and checks

```bash
# backend/
pytest
lint-imports
ruff check .

# frontend/
npm run lint
npm run typecheck
```

## Start here

| Document | What it covers |
|---|---|
| [docs/architecture.md](docs/architecture.md) | the decisions, the repository tree, deferred features, implementation order |
| [docs/backend-boundaries.md](docs/backend-boundaries.md) | `core` vs `apps` vs `services` vs `config`, with worked examples |
| [docs/domain-model.md](docs/domain-model.md) | entities, relationships, and why they are shaped that way |
| [docs/api-conventions.md](docs/api-conventions.md) | API zones, envelopes, errors, pagination, endpoint list |
| [docs/frontend-architecture.md](docs/frontend-architecture.md) | route groups, feature modules, state, pages |

More detail on each side is in [backend/README.md](backend/README.md) and
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
