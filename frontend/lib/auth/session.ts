/**
 * Session helpers.
 *
 * Authentication is a Django session cookie. The browser never holds a token,
 * and `middleware.ts` only checks for cookie *presence* to decide whether a
 * route is worth rendering - the backend remains the sole authority on who a
 * request actually is.
 */

import { cookies, headers } from "next/headers";

import { apiGet, isApiError } from "@/lib/api";
import type { Account } from "@/types/account";

export const SESSION_COOKIE = "sessionid";

/** Forwards the incoming cookie header so a server component's fetch is authenticated. */
export async function forwardedCookie(): Promise<string | undefined> {
  return (await headers()).get("cookie") ?? undefined;
}

export async function hasSessionCookie(): Promise<boolean> {
  return (await cookies()).has(SESSION_COOKIE);
}

/**
 * The signed-in account, or null.
 *
 * Server-side only, and uncached on purpose: an account's roles change what
 * the dashboard renders, so a stale answer here is a correctness bug.
 */
export async function getAccount(): Promise<Account | null> {
  if (!(await hasSessionCookie())) return null;
  try {
    return await apiGet<Account>("/client/auth/session/", {
      cache: "no-store",
      cookie: await forwardedCookie(),
    });
  } catch (error) {
    if (isApiError(error) && (error.isUnauthenticated || error.isNotFound)) return null;
    throw error;
  }
}
