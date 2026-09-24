import type { Metadata } from "next";

/** `/account` - overview: profile summary, recent requests, current plan. */

export const metadata: Metadata = { title: "My account" };

export default function AccountPage() {
  return (
    <div>
      <h1>My account</h1>
      {/* summary cards linking to the sections below */}
    </div>
  );
}
