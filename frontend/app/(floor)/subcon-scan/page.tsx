"use client";

// Floor station: Sub-con Receiving Scan
// Same pattern as gate-entry/page.tsx — see notes there. Backend
// enforces that a DC must have already cleared Gate Entry before it
// can be scanned in here (physical sequence dependency).

import { AlertCircle, CheckCircle2, ScanLine } from "lucide-react";
import { useState } from "react";
import { useScannerInput } from "@/hooks/useScannerInput";
import { apiClient } from "@/lib/api-client";

type ScanState =
  | { status: "idle" }
  | { status: "processing" }
  | { status: "success"; message: string }
  | { status: "error"; message: string };

export default function SubconScanPage() {
  const [state, setState] = useState<ScanState>({ status: "idle" });

  async function handleScan(code: string) {
    setState({ status: "processing" });
    try {
      const res = await apiClient.post<{ dc_no: string; vendor_name: string; message: string }>(
        "/receiving/subcon-scan",
        { dc_no: code }
      );
      setState({ status: "success", message: res.data.message });
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Scan failed. Try again.";
      setState({ status: "error", message: detail });
    } finally {
      setTimeout(() => setState({ status: "idle" }), 4000);
    }
  }

  useScannerInput(handleScan);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg p-6 text-center">
      <div
        className={`mb-4 flex h-14 w-14 items-center justify-center rounded-full transition-colors ${
          state.status === "success"
            ? "bg-success-bg text-success"
            : state.status === "error"
            ? "bg-error-bg text-error"
            : "bg-primary-light text-primary"
        }`}
      >
        {state.status === "success" ? (
          <CheckCircle2 className="h-7 w-7" />
        ) : state.status === "error" ? (
          <AlertCircle className="h-7 w-7" />
        ) : (
          <ScanLine className="h-7 w-7" />
        )}
      </div>

      <h1 className="mb-1 text-2xl font-semibold text-text-primary">Sub-con Receiving</h1>

      {state.status === "idle" && (
        <p className="text-text-secondary">Scan the White Box QR to log receiving.</p>
      )}
      {state.status === "processing" && <p className="text-text-secondary">Logging receipt...</p>}
      {state.status === "success" && (
        <p className="max-w-xs text-success-text">{state.message}</p>
      )}
      {state.status === "error" && <p className="max-w-xs text-error-text">{state.message}</p>}
    </div>
  );
}