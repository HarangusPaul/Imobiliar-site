# components/layout

Structural chrome shared across route groups.

| Component | Used by |
|---|---|
| `Header` | public and client layouts: navigation, search entry, account menu |
| `Footer` | public layout |
| `PublicShell` | wraps `(public)`: header, main, footer |
| `AuthShell` | wraps `(auth)`: centred card, no site navigation |
| `AccountShell` | wraps `(client)`: header plus the account sidebar |
| `DashboardShell` | wraps `dashboard`: sidebar, top bar, content area |
| `Sidebar` | the generic collapsible sidebar both shells build on |
| `Container` | max-width content wrapper |

## Shells and route groups

Each route group has exactly one shell, mounted in that group `layout.tsx`.
The dashboard is a plain segment rather than a group precisely because
`/dashboard` is a real URL prefix and its shell has nothing in common with the
public site.

Shells are server components. They receive the account as a prop from the
layout that fetched it, rather than fetching it themselves, so a page renders
with one account lookup instead of one per shell.
