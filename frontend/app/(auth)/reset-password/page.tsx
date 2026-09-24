"use client";

// M1 Forgot Password — step 2: set a new password using the token from
// the emailed reset link (?token=...).

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("This reset link is missing its token. Please request a new one.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.post("/auth/reset-password", { token, new_password: newPassword });
      router.push("/login?reset=1");
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail[0]?.msg ?? "Failed to reset password."
          : "Failed to reset password."
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
          <h1 className="text-lg font-semibold text-text-primary">Reset password</h1>
          <p className="mt-1 text-sm text-text-secondary">Choose a new password for your account.</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-border bg-surface p-6 shadow-sm"
        >
          {!token && (
            <p className="mb-4 text-sm text-error" role="alert">
              This reset link is missing its token.{" "}
              <Link href="/forgot-password" className="underline">
                Request a new one
              </Link>
              .
            </p>
          )}

          <div className="mb-4">
            <Input
              label="New Password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              placeholder="At least 8 characters"
              required
              autoFocus
            />
          </div>

          <div className="mb-1">
            <Input
              label="Confirm New Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
          </div>

          {error && (
            <p className="mb-1 mt-3 text-sm text-error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" loading={submitting} className="mt-5 w-full">
            {submitting ? "Resetting..." : "Reset password"}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordForm />
    </Suspense>
  );
}
