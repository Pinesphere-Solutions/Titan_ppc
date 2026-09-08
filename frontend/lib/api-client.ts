// Typed API client — wraps calls to the FastAPI backend.
// Base URL comes from env config so dev/staging/prod point at different
// backends without a code change. See architecture doc Section 5.1.

import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  withCredentials: true, // sends the httpOnly auth cookie
});

// TODO: add a response interceptor that redirects to /login on 401,
// and a request interceptor if a CSRF token needs to be attached.
