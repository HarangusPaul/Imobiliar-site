import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  // The browser never calls the Django origin directly. Requests go to
  // /api/backend/* on this origin and are proxied, so the session cookie is
  // first-party and lib/api needs no CORS handling.
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${process.env.BACKEND_ORIGIN ?? "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },
};

export default config;
