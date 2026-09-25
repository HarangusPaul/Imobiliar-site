import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  // Django URLs end in a slash. Without this, Next.js 308-redirects
  // /api/backend/x/ to /api/backend/x, which breaks every POST.
  skipTrailingSlashRedirect: true,
  // The browser never calls the Django origin directly. Requests go to
  // /api/backend/* on this origin and are proxied, so the session cookie is
  // first-party and lib/api needs no CORS handling.
  async rewrites() {
    const backend = `${process.env.BACKEND_ORIGIN ?? "http://localhost:8000"}/api/v1`;
    return [
      // The first rule keeps the trailing slash, which `:path*` alone drops.
      { source: "/api/backend/:path*/", destination: `${backend}/:path*/` },
      { source: "/api/backend/:path*", destination: `${backend}/:path*` },
    ];
  },
};

export default config;
