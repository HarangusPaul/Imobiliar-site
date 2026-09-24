import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { getAccount } from "@/lib/auth/session";
import { routes } from "@/lib/constants/routes";

/**
 * Client route group: the signed-in user's own area.
 *
 * `middleware.ts` has already turned away visitors with no session cookie.
 * This layout does the real check by fetching the account, which also makes it
 * the single place the account is loaded for the whole section.
 */

export default async function ClientLayout({ children }: { children: ReactNode }) {
  const account = await getAccount();
  if (!account) redirect(routes.login);

  return (
    <>
      {/* <AccountShell account={account}> with <AccountNav /> */}
      <main>{children}</main>
    </>
  );
}
