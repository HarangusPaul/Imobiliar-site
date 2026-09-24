# features/properties

Everything the interface knows about listings.

## Contents

| File | Responsibility |
|---|---|
| `api.ts` | every property request, wrapping `lib/api`. No other file issues one. |
| `types.ts` | `PropertyCard`, `PropertyDetail`, `DashboardPropertyRow`, filter shapes |
| `components/PropertyCard.tsx` | the grid tile |
| `components/PropertyGrid.tsx` | results layout with empty and loading states |
| `components/PropertyGallery.tsx` | detail-page gallery and lightbox |
| `components/PropertyFacts.tsx` | rooms / area / floor / year block |
| `components/PropertyFilterPanel.tsx` | the filter sidebar (see below) |
| `components/PropertyForm.tsx` | dashboard create/edit form |
| `format.ts` | price, area and floor formatting for display |

## The card/detail split

`PropertyCard` carries no description, no gallery and no documents, mirroring
the backend serializer. A search page returning 24 results must stay one small
response; if a card needs a new field, the backend `for_card()` queryset and
the public serializer change together with this type.

## Where the boundary sits

Property-specific UI lives here, not in `components/ui`. `PropertyCard` may
compose the generic `Badge` and `Card`; `Badge` must never know what
`availability_status` means.

Filters are rendered here but not decided here: which facets exist, and which
of them require a subscription, comes from the backend. The panel renders what
it is given and disables premium facets for accounts that lack the entitlement.
