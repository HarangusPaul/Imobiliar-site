# API conventions

## Zones

```
/api/v1/public/      unauthenticated website data
/api/v1/client/      authenticated end-user account actions
/api/v1/dashboard/   agent and staff operations
/api/v1/internal/    restricted internal functions, closed by default
```

The zone is part of the contract, not a namespace convenience. A resource
exposed publicly and the same resource exposed to the dashboard are **two
endpoints** with different serializers, different querysets and different
permissions. One endpoint that reshapes itself based on who is asking is the
pattern this design exists to avoid: it is where field-leak bugs live.

`/internal/` is empty on purpose. It exists so restricted functions have an
obvious home the day they are needed instead of being improvised into the
dashboard zone, and its default permission is `core.permissions.DenyAll`.

## Envelopes

Success:

```json
{ "data": { "...": "..." } }
```

Success with metadata (all list endpoints):

```json
{
  "data": [ { "...": "..." } ],
  "meta": { "count": 412, "page": 1, "pages": 18, "page_size": 24,
            "next": "...", "previous": null }
}
```

Failure - every failure, from validation to 500:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The submitted data is invalid.",
    "details": { "price": ["A sale price below 1000 looks like a data-entry error."] },
    "request_id": "9f2c1a..."
  }
}
```

`code` is stable and machine-readable; `message` is for humans; `details`
carries field errors for validation failures; `request_id` matches the
`X-Request-ID` response header and the server log line.

Produced by `core/api/responses.py` and `core/api/exceptions.py`. Views never
hand-build a response body.

## Error codes

| Code | Status | Meaning |
|---|---|---|
| `validation_error` | 400 | field-level problems in `details` |
| `invalid_credentials` | 400 | login failed (never says which part) |
| `not_authenticated` | 401 | no session |
| `permission_denied` | 403 | role or entitlement insufficient |
| `not_allowed` | 403 | the action is not permitted for this actor |
| `not_found` | 404 | absent, or not visible to this caller |
| `conflict` | 409 | state conflict, e.g. an illegal transition |
| `throttled` | 429 | rate limit |
| `server_error` | 500 | unhandled |

Domain apps raise `DomainError` subclasses with their own codes
(`invalid_publication_transition`, `verification_expired`,
`unsupported_media_type`, …). The handler turns them into the envelope; app
code never formats HTTP.

## Identifiers

- **Public URLs use slugs.** `/public/properties/two-room-apartment-cluj/`
- **Authenticated URLs use UUIDs.** `/dashboard/properties/{uuid}/`
- **Database ids are never exposed.**

The dashboard uses UUIDs because it must reach drafts and archived listings
whose slugs may be absent or changing, and internal URLs have no SEO reason to
be readable.

## Pagination

`DefaultPageNumberPagination` for browsable result sets - the public property
grid, where visitors expect page numbers and a total count. Default page size
24, maximum 100 via `page_size`.

`TimelineCursorPagination` for large append-only feeds such as audit events and
lead history, where deep offsets degrade and a total count is not worth the
second query.

## Endpoint scaffold

| Method | Path | Notes |
|---|---|---|
| POST | `/api/v1/client/auth/register/` | phone + password; anonymous only; throttled |
| POST | `/api/v1/client/auth/login/` | opens a session; one error for every failure |
| POST | `/api/v1/client/auth/logout/` | 204 |
| GET | `/api/v1/public/properties/` | paginated search; card serializer |
| GET | `/api/v1/public/properties/{slug}/` | detail; `meta.similar` carries related cards |
| GET | `/api/v1/public/developments/` | paginated; annotated with unit counts and price-from |
| GET | `/api/v1/public/developments/{slug}/` | full hierarchy in one response |
| POST | `/api/v1/public/leads/` | contact form; scoped throttle; honeypot |
| GET | `/api/v1/dashboard/properties/` | scoped by capability |
| POST | `/api/v1/dashboard/properties/create/` | requires `properties.create` |
| GET | `/api/v1/dashboard/leads/` | scoped inbox; `meta.counts` for badges |

### Public property search parameters

`q`, `transaction_type`, `property_type` (repeatable), `city`, `neighborhood`
(repeatable), `price_min`, `price_max`, `currency`, `rooms_min`, `rooms_max`,
`area_min`, `area_max`, `floor_min`, `floor_max`, `year_built_min`, `features`
(repeatable), `featured`, `sort`, `page`, `page_size`.

`sort` accepts only `newest`, `price_asc`, `price_desc`, `area_desc`,
`featured`. An unknown value falls back to the default rather than erroring, so
a stale bookmark still works and no column name can be injected.

Premium feature filters are **silently dropped** for callers without the
entitlement rather than rejected. A shared or bookmarked search URL keeps
working for everyone; unentitled visitors simply see a broader result set.

## Response shape discipline

Public list responses never include descriptions, galleries, documents or
layouts. This is enforced in three places that must change together:
`Property.objects.for_card()`, `PropertyCardSerializer`, and the frontend
`PropertyCard` type.

Detail responses gate individual fields by entitlement: `documents` is empty
without `full_documents`, and `exact_address` is null unless the address is
public or the plan includes `subscriber_only_fields`. The gating happens
server-side, before the data leaves the process.

## View structure

```python
class SomeView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsDashboardUser, HasCapability]
    required_capability = Capability.PROPERTY_CREATE

    def post(self, request):
        serializer = InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = some_service(Input(**serializer.validated_data), actor=request.user)
        return created(OutputSerializer(obj).data)
```

- Validate, call **one** service, serialize. Nothing else.
- Reads go through a selector, never an inline queryset.
- `HasCapability` fails closed: a view that forgets `required_capability`
  grants nothing.

## Authentication

Session cookie. The frontend proxies browser requests through
`/api/backend/*` on its own origin, so the cookie is first-party and CORS does
not enter the picture. Server components forward the incoming cookie header
explicitly.

## Throttling

Anonymous callers: 120/hour by default. The lead endpoint has its own
`lead-submit` scope at 10/hour - a contact form is the most abused endpoint on
a property site. Auth endpoints use the anonymous throttle.

## Request correlation

`RequestIDMiddleware` accepts or generates an `X-Request-ID`, echoes it on the
response, stamps it on every log record, includes it in every error envelope,
and stores it on every audit event and lead. One id ties a user-visible failure
to the server logs and to what changed in the database.

## Versioning

The version is in the path. `/api/v2/` will be added as a parallel tree when a
breaking change is needed; v1 endpoints are not reshaped in place.
