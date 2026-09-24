# components/shared

Components that are not generic enough for `ui/` but are used by more than one
feature.

| Component | Why it is here |
|---|---|
| `Price` | currency and rent-period formatting, used by properties and developments |
| `AreaValue` | square-metre formatting with the same rounding everywhere |
| `PhoneLink` | `tel:` link with consistent display formatting |
| `MediaImage` | `next/image` wrapper handling backend media URLs and alt text |
| `EmptyResults` | shared empty state for search and inbox |
| `ErrorBoundaryFallback` | consistent error surface for route segments |
| `ConfirmDialog` | destructive-action confirmation built on `ui/Modal` |

## The test for this folder

Two or more features use it, and it carries some domain awareness.

One feature only? It belongs to that feature. No domain awareness at all? It
belongs in `ui/`. `Price` is the canonical example: it knows that a rental
shows a period suffix and that price-on-request renders as text, which
disqualifies it from `ui/`, but properties, developments and the dashboard all
need it.
