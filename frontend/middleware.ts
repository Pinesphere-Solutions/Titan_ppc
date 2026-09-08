import { NextRequest, NextResponse } from "next/server";

// Guards all (dashboard) and (floor) routes. Checks for the presence of the
// httpOnly auth cookie set by the backend on login. Actual token validity
// is re-checked server-side on every API call (see architecture doc
// Section 7.1) — this middleware only handles the redirect-to-login UX.

const PROTECTED_PREFIXES = [
  "/dashboard",
  "/sap-outward",
  "/receiving",
  "/dc-verification",
  "/physical-verification",
  "/deviations",
  "/qc-acknowledgement",
  "/sap-processing",
  "/ppc-collection",
  "/qa-inspection",
  "/zqmtl1",
  "/storage",
  "/reports",
  "/masters",
  "/settings",
  "/gate-entry",
  "/subcon-scan",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((p) => pathname.startsWith(p));

  if (!isProtected) {
    return NextResponse.next();
  }

  const token = request.cookies.get("access_token");
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/sap-outward/:path*",
    "/receiving/:path*",
    "/dc-verification/:path*",
    "/physical-verification/:path*",
    "/deviations/:path*",
    "/qc-acknowledgement/:path*",
    "/sap-processing/:path*",
    "/ppc-collection/:path*",
    "/qa-inspection/:path*",
    "/zqmtl1/:path*",
    "/storage/:path*",
    "/reports/:path*",
    "/masters/:path*",
    "/settings/:path*",
    "/gate-entry/:path*",
    "/subcon-scan/:path*",
  ],
};
