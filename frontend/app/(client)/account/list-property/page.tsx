import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { PageHead } from "@/components/shared/PageHead";
import { ListPropertyForm } from "@/features/listing/components/ListPropertyForm";
import { getAccount } from "@/lib/auth/session";
import { routes } from "@/lib/constants/routes";

/**
 * `/account/list-property` - an owner submits a property for advisor review.
 *
 * The layout has already required a session; the account is read again here
 * (same request, no extra cost worth caching) to prefill the contact section.
 */

export const metadata: Metadata = { title: "List a property" };

export default async function ListPropertyPage() {
  const account = await getAccount();
  if (!account) redirect(`${routes.login}?next=${encodeURIComponent(routes.account.listProperty)}`);

  return (
    <>
      <PageHead title="List a property">
        Answer each section and save as you go. An advisor reviews every listing before it goes live,
        usually within two working days.
      </PageHead>
      <ListPropertyForm account={account} />
    </>
  );
}
