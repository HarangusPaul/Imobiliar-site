import { apiList, apiPost, type Paginated, type RequestOptions } from "@/lib/api";

import type { DashboardLeadRow, LeadReceipt, LeadSubmission } from "./types";

/** Public contact form. Rate-limited server-side. */
export function submitLead(input: LeadSubmission): Promise<LeadReceipt> {
  return apiPost<LeadReceipt>("/public/leads/", input);
}

export function fetchDashboardLeads(
  params: { status?: string; assigned?: string; page?: string } = {},
  options: RequestOptions = {},
): Promise<Paginated<DashboardLeadRow>> {
  return apiList<DashboardLeadRow>("/dashboard/leads/", {
    query: params,
    cache: "no-store",
    ...options,
  });
}
