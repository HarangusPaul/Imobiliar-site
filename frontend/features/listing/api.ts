import { apiPost } from "@/lib/api";
import { routes } from "@/lib/constants/routes";

/**
 * Owner listing submissions travel as a lead to the advisors' inbox until the
 * backend has a dedicated endpoint (see model.ts). Swapping the endpoint is a
 * change to this file only.
 */

export interface ListingSubmission {
  full_name: string;
  phone_number: string;
  email?: string;
  message: string;
}

export interface ListingReceipt {
  id: string;
  status: string;
  created_at: string;
}

export function submitListing(input: ListingSubmission): Promise<ListingReceipt> {
  return apiPost<ListingReceipt>("/public/leads/", {
    ...input,
    kind: "valuation",
    contact_preference: "phone",
    source_path: routes.account.listProperty,
    website: "",
  });
}
