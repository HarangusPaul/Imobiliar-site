import type { Metadata } from "next";

import { PageHead } from "@/components/shared/PageHead";
import { collectionOrder } from "@/features/collections/data";
import { ContactDetails } from "@/features/leads/components/ContactDetails";
import { ContactForm } from "@/features/leads/components/ContactForm";
import { getAccount } from "@/lib/auth/session";

import styles from "./contact.module.css";

/**
 * `/contact` - the general contact form beside the office details.
 *
 * Submission posts to the public lead endpoint, which is rate-limited and
 * honeypot-protected server-side. A signed-in visitor gets their name and
 * number prefilled. `?topic=` and `?listing=` preselect the form, so other
 * pages can link straight to a relevant enquiry.
 */

export const metadata: Metadata = {
  title: "Contact us",
  description: "Send a message and an advisor will get back to you personally.",
};

interface PageProps {
  searchParams: Promise<{ topic?: string; listing?: string }>;
}

const listingOptions = collectionOrder.flatMap((collection) =>
  collection.listings.map((listing) => ({
    value: listing.id,
    label: `${listing.name} — ${listing.location}`,
  })),
);

export default async function ContactPage({ searchParams }: PageProps) {
  const [{ topic, listing }, account] = await Promise.all([searchParams, getAccount()]);

  return (
    <>
      <PageHead title="Contact us">
        Looking for somewhere that isn’t listed, or ready to arrange a viewing? Send a message and
        an advisor will get back to you personally.
      </PageHead>
      <div className={styles.layout}>
        <div className={styles.form}>
          <ContactForm
            account={account}
            listings={listingOptions}
            initialTopic={topic}
            initialListing={listing}
          />
        </div>
        <ContactDetails />
      </div>
    </>
  );
}
