"use client";

// M1 Login — redesigned using the shared component library. Logic
// unchanged: same POST /auth/login call, same redirect-on-success, same
// session-expired handling from the api-client 401 interceptor.

import { AlertCircle, Eye, EyeOff } from "lucide-react";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionExpired = searchParams.get("expired") === "1";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await apiClient.post("/auth/login", { username, password });
      router.push("/dashboard");
      router.refresh();
    } catch {
      setError("Invalid username or password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-lg font-bold text-white">
            P
          </div>
          <h1 className="text-lg font-semibold text-text-primary">PPC CBE Tracking Application</h1>
          <p className="mt-1 text-sm text-text-secondary">Sign in to continue</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-border bg-surface p-6 shadow-sm"
        >
          {sessionExpired && (
            <div className="mb-4 flex items-start gap-2 rounded-md bg-warning-bg px-3 py-2.5 text-sm text-warning-text">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>Your session expired. Please sign in again.</span>
            </div>
          )}

          <div className="mb-4">
            <Input
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              autoFocus
            />
          </div>

          <div className="mb-1 relative">
            <Input
              label="Password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              className="pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword((s) => !s)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="absolute right-3 top-[34px] text-text-muted hover:text-text-secondary"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {error && (
            <p className="mb-1 mt-3 text-sm text-error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" loading={submitting} className="mt-5 w-full">
            {submitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  // useSearchParams requires a Suspense boundary in the App Router.
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}