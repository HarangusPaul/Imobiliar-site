/**
 * Client-side role helpers - for *rendering*, never for security.
 *
 * Hiding a dashboard link from a client account is a UX decision. The backend
 * enforces the same rule again on every request (`apps/access`), and that is
 * the check that matters.
 */

import type { Account } from "@/types/account";

export const ROLE = {
  CLIENT: "client",
  AGENT: "agent",
  STAFF: "staff",
} as const;

export type RoleCode = string;

export function hasRole(account: Account | null, role: RoleCode): boolean {
  return Boolean(account?.roles.includes(role));
}

/** Roles that may open the dashboard shell at all. */
export function canOpenDashboard(account: Account | null): boolean {
  return hasRole(account, ROLE.AGENT) || hasRole(account, ROLE.STAFF);
}

export function isStaff(account: Account | null): boolean {
  return hasRole(account, ROLE.STAFF);
}
