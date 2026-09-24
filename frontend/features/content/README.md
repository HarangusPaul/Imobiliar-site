# features/content

Presentation pages and SEO metadata.

| File | Responsibility |
|---|---|
| `api.ts` | fetch a presentation page by slug |
| `types.ts` | `PresentationPage` and SEO metadata shapes |
| `metadata.ts` | build a Next.js `Metadata` object from backend SEO fields |
| `components/PageBody.tsx` | render a presentation page body |
| `components/Hero.tsx` | the homepage hero block |

## Intentionally small

The backend keeps `apps/content` minimal and so does this feature. It is not a
page builder. The about and contact pages render structured content; everything
else is a route with hand-built layout.

## SEO

`metadata.ts` is the one place that turns backend SEO fields into a `Metadata`
export, with fallbacks to the object title and description. Property and
development pages use it too, which is why it lives here rather than inside
either of those features.
