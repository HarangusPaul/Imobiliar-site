import type { LeadStatus } from "@/lib/constants/domain";

export type LeadKind = "general" | "property" | "development" | "viewing" | "valuation";

export interface LeadSubmission {
  full_name: string;
  phone_number: string;
  email?: string;
  message?: string;
  kind?: LeadKind;
  contact_preference?: "phone" | "sms" | "email" | "any";
  preferred_time?: string;
  /** Subjects are referenced by their public slug, never by database id. */
  property_slug?: string;
  development_slug?: string;
  source_path?: string;
  /** Honeypot. Rendered hidden and always submitted empty by a real browser. */
  website?: string;
}

/** All a public caller gets back. No assignment or internal state. */
export interface LeadReceipt {
  id: string;
  status: LeadStatus;
  created_at: string;
}

export interface DashboardLeadRow {
  id: string;
  kind: LeadKind;
  status: LeadStatus;
  full_name: string;
  phone_number: string;
  email: string;
  subject_label: string | null;
  assigned_to_name: string | null;
  created_at: string;
  first_response_at: string | null;
}
