# features/search

The search experience itself, independent of what is being searched.

| File | Responsibility |
|---|---|
| `useSearchParamsState.ts` | read/write filters as URL query parameters |
| `api.ts` | facet data (cities, neighborhoods, feature groups) |
| `components/SearchBar.tsx` | the hero search input |
| `components/FilterChips.tsx` | active filters, each removable |
| `components/SortSelect.tsx` | ordering, restricted to the backend's allowed values |
| `components/ResultsHeader.tsx` | result count and sort controls |

## URL as the state container

Filter state lives in the query string, not in React state or a store. A
property search is something users share, bookmark and reach from Google;
keeping it in the URL makes that work and makes the server component able to
render the first page without any client-side fetch.

`features/properties` owns the *property-specific* filter inputs. This module
owns the mechanics of turning them into a URL and back.

## Premium filters

Some facets require a subscription entitlement. The backend silently ignores a
premium filter the caller has not paid for rather than erroring, which means a
shared URL keeps working for everyone. The UI reflects that: unentitled facets
render disabled with an upgrade hint instead of disappearing.
