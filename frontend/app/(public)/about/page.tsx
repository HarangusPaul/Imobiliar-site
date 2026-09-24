import type { Metadata } from "next";

/**
 * `/about` - company presentation.
 *
 * Content comes from `apps/content` as a presentation page, keyed by slug.
 * Deliberately not a CMS: a small set of static pages with editable bodies.
 */

export const metadata: Metadata = {
  title: "About us",
};

export default function AboutPage() {
  return (
    <div>
      <h1>About us</h1>
      {/* <PageBody slug="about" /> from features/content */}
    </div>
  );
}
