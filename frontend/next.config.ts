import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */

  // Hide the Next.js dev-mode indicator (the floating "N" badge with route/
  // bundler info) — cosmetic only, but distracting while sharing the app
  // for review over a tunnel.
  devIndicators: false,

  // Proxy API calls through the Next.js server itself so the browser only
  // ever talks to ONE origin (this frontend's own domain). This avoids two
  // problems when the app is shared over a tunnel with the frontend and
  // backend on different tunnel hostnames:
  //   1. CORS — no cross-origin request is made at all from the browser.
  //   2. Auth cookie visibility — the httpOnly access_token cookie set on
  //      login is scoped to whichever origin sent the response. Without
  //      this proxy, that's the backend's tunnel hostname, which the
  //      frontend's own middleware.ts (running against the frontend's
  //      hostname) can never see, causing an infinite /login <-> /dashboard
  //      redirect loop. With the proxy, the response (and its Set-Cookie
  //      header) comes back through the frontend's own origin, so the
  //      cookie lands where middleware.ts actually looks for it.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
