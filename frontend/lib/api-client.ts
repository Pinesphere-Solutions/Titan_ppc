// Typed API client — wraps calls to the FastAPI backend.
// Base URL comes from env config so dev/staging/prod point at different
// backends without a code change. See architecture doc Section 5.1.

import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  withCredentials: true, // sends the httpOnly auth cookie
});

// A 401 here means the access token is missing or expired — there is no
// silent refresh flow yet (see architecture doc Section 7.1's refresh

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Avoid a redirect loop if the 401 came from the login attempt itself.
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login?expired=1";
      }
    }
    return Promise.reject(error);
  }
);