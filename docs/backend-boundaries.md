# core vs apps vs services

## The rule

```
core  <-  apps
  ^
services

config composes everything
```

| Layer | May import | Must never import |
|---|---|---|
| `core` | third-party, stdlib | `apps`, `services`, `config` |
| `apps` | `core`, other `apps` (sparingly) | `services` |
| `services` | `core` contracts | `apps`, `config` |
| `config` | everything | - |

Enforced two ways: `lint-imports` from `pyproject.toml`, and
`backend/tests/test_architecture_boundaries.py` so a plain `pytest` catches a
violation too.

## How apps reach an implementation without importing one

`apps/leads` must send a notification but may not import `services`. The seam:

```python
# apps/leads/services/intake.py
from core.contracts.registry import notification_service

notification_service().send(message)
```

`core.contracts.registry` reads `settings.SERVICE_PROVIDERS`, imports the
dotted path at call time, verifies it satisfies the protocol, and caches the
instance. There is no static import edge from `core` or `apps` into `services`
anywhere in the codebase. `config/settings/base.py` is the only file that names
an implementation.

## What belongs in core

Domain-neutral project primitives. The test: *would this still make sense in a
project that is not about real estate?*

| Module | Contents |
|---|---|
| `core/models.py` | `UUIDModel`, `TimestampedModel`, `BaseModel`, soft-delete base |
| `core/api/pagination.py` | page-number and cursor paginators |
| `core/api/exceptions.py` | `DomainError` base, the uniform error envelope, the DRF handler |
| `core/api/responses.py` | the success envelope |
| `core/middleware.py` | request id, security headers |
| `core/logging.py` | request-id contextvar and logging filter |
| `core/permissions.py` | `IsAuthenticatedAndActive`, `IsOwner`, `ReadOnly`, `DenyAll` |
| `core/validation.py` | phone normalisation, slug generation, numeric parsing |
| `core/security.py` | code generation, keyed hashing, phone masking |
| `core/tasks.py` | the deferred-work base class |
| `core/contracts/` | notification, verification, storage, analytics protocols and the resolver |

Not in core: `Property`, `Lead`, `Subscription`, `Role`, `Agent`, `Apartment`,
price validation, OTP expiry policy, lead status transitions.

`core/validation.py` deserves a note. It normalises a phone number because
that is a *syntactic* concern shared by accounts, leads and contact forms. It
does not know that a phone number is a login identifier - that is
`apps/accounts`.

## What belongs in apps

| App | Owns |
|---|---|
| `accounts` | the custom user model, phone identity, password auth, registration/login/logout, verification-code state and policy, account status |
| `access` | roles, role assignment, capabilities, area access; roles are rows, so new ones need no code change |
| `subscriptions` | plans, subscription state, entitlements, and the single answer to "may this user access X" |
| `locations` | country, city, neighborhood, address, coordinates, public vs exact address visibility |
| `properties` | listings, types, the three state axes, characteristics, price, features, agent link, public search and detail |
| `developments` | projects, buildings, floors, unit types, units, inventory availability, and the unit-to-listing link |
| `media` | media metadata, category, alt text, ordering, and attachment to any owner. Never bytes |
| `leads` | contact and enquiry forms, status flow, assignment, notes, notification decisions |
| `audit` | append-only events: who did what to which object, in which request |
| `content` | SEO metadata foundations and minimal presentation pages. Not a CMS |

Standard app layout:

```
apps/<domain>/
├── admin.py          Django Admin registration
├── apps.py
├── models/           schema and invariants
├── api/
│   ├── serializers/  input validation and output shaping, per zone
│   ├── views/        thin; validate, call a service, serialize
│   └── urls.py       one urlpatterns list per API zone
├── services/         write workflows and transaction boundaries
├── selectors/        read/query logic
├── permissions.py    domain-specific permission classes
├── tasks.py          deferred work
├── tests/
└── migrations/
```

## What belongs in services

Replaceable adapters, one folder per contract, plus `registry.py` declaring
what this repository ships. Every implementation in this phase is local:
console notification, console verification, local-filesystem storage, no-op
analytics.

A service must be meaningless outside its contract. If a module under
`services/` mentions a listing, a lead or a plan, it is in the wrong layer.

## Worked examples

| Requirement | Correct location | Incorrect location |
|---|---|---|
| UUID and timestamps base class | `core/models.py` | duplicated inside all apps |
| Property price validation | `apps/properties/validators.py` | `core` |
| Property filter/search logic | `apps/properties/selectors/search.py` | `services/search` |
| Lead status flow | `apps/leads/services/workflow.py` | `services/notifications` |
| Deciding if a lead should notify an agent | `apps/leads/services/intake.py` | `services/notifications` |
| Sending a notification | `services/notifications` | `apps/leads` directly |
| OTP expiry and verification attempts | `apps/accounts` | `services/verification` |
| Delivering an OTP | `services/verification` | `apps/accounts` |
| Media categories and property-media relation | `apps/media` | `services/storage` |
| Actual file write/read operation | `services/storage` | `apps/media` |
| Subscription entitlement check | `apps/subscriptions/selectors/entitlements.py` | `services` |
| Generic API pagination | `core/api/pagination.py` | `apps/properties` duplicated |
| User's role access policy | `apps/access` | `core` |
| Request ID middleware | `core/middleware.py` | a random app |

## No dumping grounds

`utils.py`, `helpers.py`, `common.py` and `misc.py` do not exist anywhere and a
test asserts it. Every module name states what it owns: `validation.py`,
`security.py`, `publishing.py`, `intake.py`, `entitlements.py`.

When something has no obvious home, that is a signal the concept is missing,
not that a junk drawer is needed.

## Cross-app imports

Apps may import each other, but sparingly and in one direction where possible:

- `properties` and `leads` ask `access` about capabilities.
- `properties` and `leads` record events through `audit`.
- `accounts` assigns a default role through `access`, using a function-local
  import so there is no import-time cycle.
- `developments` reads `properties` enums to map inventory state to listing
  state.

Anything heavier than this is a sign two apps should be one, or that a concept
belongs in `core`.
