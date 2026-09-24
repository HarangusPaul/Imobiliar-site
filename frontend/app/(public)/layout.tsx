import type { ReactNode } from "react";

import { getAccount } from "@/lib/auth/session";

/**
 * Public route group: the marketing and browsing site.
 *
 * The group `(public)` does not appear in the URL, so `/`, `/properties` and
 * `/about` all live here while sharing one header and footer.
 *
 * The account is fetched once here and passed down, so the header can show a
 * name without every page repeating the lookup. Pages themselves stay
 * cacheable: only this layout is account-aware.
 */

export default async function PublicLayout({ children }: { children: ReactNode }) {
  const account = await getAccount();

  return (
    <>
      {/* <Header account={account} /> from components/layout */}
      <main>{children}</main>
      {/* <Footer /> from components/layout */}
      {account ? null : null}
    </>
  );
}
