# features/developments

Residential projects and their inventory.

| File | Responsibility |
|---|---|
| `api.ts` | development list and detail requests |
| `types.ts` | `DevelopmentCard`, `DevelopmentDetail`, `Building`, `Floor`, `Unit`, `UnitType` |
| `components/DevelopmentCard.tsx` | project tile for the index |
| `components/BuildingSelector.tsx` | switch between buildings in a project |
| `components/FloorPlanViewer.tsx` | floor plate with its units |
| `components/UnitTable.tsx` | available units, sortable by area and price |
| `components/UnitTypeGallery.tsx` | the repeated apartment layouts |

## Navigating the hierarchy

The detail response carries the whole tree. The page holds *which building and
which floor is selected* in URL state (`?building=a&floor=3`), so a chosen
floor is linkable and survives a refresh. No client store is needed for it.

## Unit vs listing

A unit links to a public listing only when `listing_slug` is non-null. The
backend sets it exclusively for units whose listing is actually published, so
the UI must not synthesise a property URL from a unit id - an unlisted unit has
no public page.
