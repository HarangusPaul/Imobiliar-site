# components/ui

Generic, domain-free building blocks.

`Button` `Input` `Select` `Checkbox` `RadioGroup` `Textarea` `Modal` `Drawer`
`Table` `Pagination` `Badge` `Card` `Tabs` `Tooltip` `Skeleton` `Spinner`
`Alert` `Breadcrumb`

## The rule

A component here must be reusable in a project that is not about real estate.

That means no imports from `features/*`, no domain vocabulary in props, and no
knowledge of backend enums. `Badge` takes `variant="success"`, never
`status="published"`. Mapping a domain value to a variant happens in the
feature that owns the domain value.

Concretely:

- `Pagination` takes `page`, `pageCount` and an `onPageChange` callback. It
  does not know that `meta.pages` came from a property search.
- `Table` takes columns and rows. Column definitions for the lead inbox live in
  `features/dashboard/components/DataTable.tsx`.
- `Modal` takes children. A confirm-archive dialog is a property component that
  renders a `Modal`.

## Why this matters

This is where a codebase usually rots first: a `PropertyBadge` here, then a
price formatter, then a fetch. Each looks harmless, and together they make the
generic layer unusable and untestable. If a component needs a domain type in
order to compile, it is in the wrong folder.
