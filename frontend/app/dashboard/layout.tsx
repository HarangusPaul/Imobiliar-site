import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { canOpenDashboard } from "@/lib/auth/roles";
import { getAccount } from "@/lib/auth/session";
import { routes } from "@/lib/constants/routes";

/**
 * Dashboard segment.
 *
 * Not a route group: `/dashboard` is a real URL prefix, and its chrome has
 * nothing in common with the public site.
 *
 * Two checks, neither of which is the last word. `middleware.ts` handles the
 * no-cookie case; this layout rejects accounts without a dashboard role. The
 * authoritative check is `apps/access` on every backend request - a client who
 * forced their way to this shell would see an empty, erroring dashboard.
 */

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const account = await getAccount();
  if (!account) redirect(routes.login);
  if (!canOpenDashboard(account)) redirect(routes.account.root);

  return (
    <>
      {/* <DashboardShell account={account}> with <DashboardNav /> */}
      <main>{children}</main>
    </>
  );
}
