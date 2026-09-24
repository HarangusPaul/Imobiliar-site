# services/storage

Reads and writes file bytes.

**Contract:** `core.contracts.storage.FileStorageService`

## What lives here

- `local.py` - filesystem-backed implementation rooted at
  `LOCAL_STORAGE_ROOT`. Generates non-enumerable keys, refuses path traversal
  outside the root, and computes a checksum on write.

## What must never live here

- Media categories, alt text, sort order, or which property a file belongs to.
  All of that is `apps/media`.
- Image derivative *policy* (which thumbnail sizes a property gallery needs).
  A future implementation may perform the work, but the sizes are a media-domain
  decision passed in by the caller.
- Permission checks about who may see a file. Access policy is `apps/access`
  plus `apps/subscriptions`.

## Contract notes

`save()` takes a `namespace` - a caller-chosen logical folder such as
`properties/gallery` or `developments/units/layouts`. The service treats it as
an opaque path segment and sanitises it; it attaches no meaning to it.

Binary content is never written to PostgreSQL. The database stores the returned
`key` only.
