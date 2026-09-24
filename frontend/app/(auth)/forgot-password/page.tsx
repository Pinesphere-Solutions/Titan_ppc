"use client";

// M1 Forgot Password — step 1: request a reset link by email. Always
// shows the same generic confirmation regardless of whether the email
// exists, matching the backend's deliberately generic response (so this
// page can't be used to check which emails have accounts).

import { useState } from "react";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await apiClient.post("/auth/forgot-password", { username: email });
      setSubmitted(true);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail[0]?.msg ?? "Please enter a valid email address."
          : "Please enter a valid email address."
      );
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
          <h1 className="text-lg font-semibold text-text-primary">Forgot password</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Enter your account email and we&apos;ll send you a reset link.
          </p>
        </div>

        <div className="rounded-lg border border-border bg-surface p-6 shadow-sm">
          {submitted ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <CheckCircle2 className="h-8 w-8 text-success" />
              <p className="text-sm text-text-primary">
                If an account exists for <span className="font-medium">{email}</span>, we&apos;ve sent a
                password reset link to it.
              </p>
              <Link href="/login" className="text-sm text-primary hover:underline">
                Back to sign in
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <Input
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="username"
                  required
                  autoFocus
                />
              </div>

              {error && (
                <p className="mb-3 text-sm text-error" role="alert">
                  {error}
                </p>
              )}

              <Button type="submit" loading={submitting} className="w-full">
                {submitting ? "Sending..." : "Send reset link"}
              </Button>

              <div className="mt-4 text-center">
                <Link href="/login" className="text-sm text-text-secondary hover:underline">
                  Back to sign in
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
