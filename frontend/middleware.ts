import { NextResponse, type NextRequest } from "next/server";

/**
 * Route-level gate.
 *
 * This checks only whether a session cookie is *present*, so an anonymous
 * visitor is redirected to the login page instead of rendering a shell that
 * will fail every data call. It is not a security boundary: the middleware
 * cannot see roles, and a forged cookie gets nowhere because the backend
 * re-checks identity and permissions on every request.
 *
 * Role-based access (agent vs staff vs client) is enforced in two places that
 * matter: the layout, which fetches the account and redirects, and
 * `apps/access` on the server.
 */

const SESSION_COOKIE = "sessionid";

/** Segments that require a session to be worth rendering at all. */
const PROTECTED_PREFIXES = ["/account", "/dashboard"];

/** Pages a signed-in user has no reason to see. */
const ANONYMOUS_ONLY = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);

  if (!hasSession && PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix))) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = `?next=${encodeURIComponent(pathname + search)}`;
    return NextResponse.redirect(url);
  }

  if (hasSession && ANONYMOUS_ONLY.includes(pathname)) {
    const url = request.nextUrl.clone();
    url.pathname = "/account";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/account/:path*", "/dashboard/:path*", "/login", "/register"],
};
