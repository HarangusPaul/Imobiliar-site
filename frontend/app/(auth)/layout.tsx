import type { ReactNode } from "react";

import { Header } from "@/components/layout/Header";

/**
 * Auth route group.
 *
 * `/login` and `/register` keep the site navigation but drop the footer: a
 * visual panel and the form card fill the rest of the screen. Signed-in
 * visitors never get here (`middleware.ts` redirects them), so the header is
 * always the signed-out one.
 */

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <Header account={null} />
      <main>{children}</main>
    </>
  );
}
