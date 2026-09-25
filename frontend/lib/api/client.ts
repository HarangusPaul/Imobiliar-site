/**
 * The single HTTP boundary of the application.
 *
 * Nothing outside `lib/api` may call `fetch` against the backend, and nothing
 * outside a feature's `api.ts` may call this client. The chain is always:
 *
 *   page/component -> features/<domain>/api.ts -> lib/api/client.ts -> backend
 *
 * That gives one place to change auth handling, one place to parse the error
 * envelope, and one place to look when a request misbehaves.
 */

import { ApiError, parseErrorBody } from "./errors";
import type { ApiEnvelope, ApiMeta, Paginated } from "./types";

/** Server components talk to the backend directly; the browser goes through the rewrite. */
const BASE_URL =
  typeof window === "undefined"
    ? `${process.env.BACKEND_ORIGIN ?? "http://localhost:8000"}/api/v1`
    : "/api/backend";

export type QueryValue = string | number | boolean | null | undefined | string[];

export interface RequestOptions {
  /** Query parameters. Arrays become repeated keys. */
  query?: Record<string, QueryValue>;
  /** JSON body. Omit for GET. */
  body?: unknown;
  /** Next.js caching. Public reads revalidate; anything user-scoped is `no-store`. */
  cache?: RequestCache;
  revalidate?: number | false;
  tags?: string[];
  signal?: AbortSignal;
  /** Forwarded from a server component so SSR requests carry the session. */
  cookie?: string;
}

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
  const url = `${BASE_URL}${path}`;
  if (!query) return url;

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") continue;
    if (Array.isArray(value)) {
      for (const item of value) if (item !== "") params.append(key, item);
    } else {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

/**
 * Django's CSRF token, read from its cookie. Session-authenticated writes need
 * it; login sets the cookie. Server-side requests forward cookies instead.
 */
function csrfToken(): string | undefined {
  if (typeof document === "undefined") return undefined;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]!) : undefined;
}

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

async function request<T>(
  method: string,
  path: string,
  options: RequestOptions = {},
): Promise<ApiEnvelope<T>> {
  const { query, body, cache, revalidate, tags, signal, cookie } = options;

  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (cookie) headers["Cookie"] = cookie;
  if (!SAFE_METHODS.has(method)) {
    const token = csrfToken();
    if (token) headers["X-CSRFToken"] = token;
  }

  let response: Response;
  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "include",
      signal,
      cache,
      next: revalidate === undefined && !tags ? undefined : { revalidate, tags },
    });
  } catch (cause) {
    throw new ApiError({
      code: "network_error",
      message: "The server could not be reached.",
      status: 0,
      cause,
    });
  }

  if (response.status === 204) return { data: undefined as T };

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    throw parseErrorBody(payload, response.status);
  }
  return payload as ApiEnvelope<T>;
}

/** Unwraps the envelope for endpoints that return a single object. */
export async function apiGet<T>(path: string, options?: RequestOptions): Promise<T> {
  return (await request<T>("GET", path, options)).data;
}

/** Keeps the envelope for list endpoints, because `meta` carries the page info. */
export async function apiList<T>(
  path: string,
  options?: RequestOptions,
): Promise<Paginated<T>> {
  const envelope = await request<T[]>("GET", path, options);
  return { items: envelope.data, meta: (envelope.meta ?? {}) as ApiMeta };
}

export async function apiPost<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  return (await request<T>("POST", path, { ...options, body, cache: "no-store" })).data;
}

export async function apiPatch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  return (await request<T>("PATCH", path, { ...options, body, cache: "no-store" })).data;
}

export async function apiDelete(path: string, options?: RequestOptions): Promise<void> {
  await request<void>("DELETE", path, { ...options, cache: "no-store" });
}
