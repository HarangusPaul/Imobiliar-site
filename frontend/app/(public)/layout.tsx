import type { ReactNode } from "react";

import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
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
      <Header account={account} />
      <main>{children}</main>
      <Footer />
    </>
  );
}
