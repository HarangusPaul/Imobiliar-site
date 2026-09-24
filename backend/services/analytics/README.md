# services/analytics

Receives business events emitted by domain apps.

**Contract:** `core.contracts.analytics.AnalyticsService`

## What lives here

- `noop.py` - accepts and discards events (debug-logged). Active by default so
  domain apps can emit events from day one with no tracking configured.

## What must never live here

- The list of which events exist. Event names are owned by the app that emits
  them (`property.viewed`, `lead.created`, `subscription.activated`).
- Any interpretation of event payloads as business facts.
- Reporting or aggregation used to make product decisions; dashboard analytics
  read from domain tables, not from this sink.

## Note on the dashboard analytics page

`/dashboard/analytics` is a deferred placeholder. When it is built it will be
served by domain selectors over domain data. This contract is about emitting
events outward, which is a separate concern.
