"use client";

// M5 DC Verification
// Client component — needs interactivity (form submission, live result
// display) unlike the read-only M3 screen. Fetches the pending DC list
// from the existing /sap-outward/list endpoint (M3's endpoint), filtered
// client-side to status === "pending", rather than building a second
// backend endpoint just for this dropdown.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface DispatchListItem {
  sap_document_no: string;
  dc_no: string | null;
  vendor_name: string;
  material_code: string;
  quantity_front_case: number | null;
  quantity_back_case: number | null;
  verification_status: string | null;
}

interface VerifyResult {
  dc_no: string;
  expected_qty: number;
  actual_qty: number;
  result: string; // "matched" | "excess" | "less"
  verification_status: string;
  deviation_created: boolean;
  deviation_id: string | null;
}

const RESULT_STYLES: Record<string, string> = {
  matched: "bg-green-100 text-green-800 border-green-300",
  excess: "bg-blue-100 text-blue-800 border-blue-300",
  less: "bg-red-100 text-red-800 border-red-300",
};

export default function DcVerificationPage() {
  const [pendingDcs, setPendingDcs] = useState<DispatchListItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [actualFrontCase, setActualFrontCase] = useState("");
  const [actualBackCase, setActualBackCase] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VerifyResult | null>(null);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<DispatchListItem[]>("/sap-outward/list");
      setPendingDcs(res.data.filter((item) => item.verification_status === "pending"));
    } catch {
      setError("Failed to load pending delivery challans.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
  }, []);

  const selectedDispatch = pendingDcs.find((d) => d.dc_no === selectedDcNo);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await apiClient.post<VerifyResult>(
        `/dc-verification/${selectedDcNo}/verify`,
        {
          actual_front_case: Number(actualFrontCase),
          actual_back_case: Number(actualBackCase),
        }
      );
      setResult(res.data);
      setSelectedDcNo("");
      setActualFrontCase("");
      setActualBackCase("");
      await loadPendingDcs(); // refresh dropdown — verified DC drops out of pending
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Verification failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M5 — DC Verification</h1>
      <p className="mb-4 text-sm text-gray-500">
        Compare physically received quantity against the expected quantity from SAP.
      </p>

      {loading ? (
        <p className="text-sm text-gray-500">Loading pending delivery challans...</p>
      ) : pendingDcs.length === 0 ? (
        <p className="text-sm text-gray-500">
          No delivery challans are currently pending verification.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="max-w-md rounded border p-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Delivery Challan
          </label>
          <select
            className="mb-3 w-full rounded border px-3 py-2 text-sm"
            value={selectedDcNo}
            onChange={(e) => setSelectedDcNo(e.target.value)}
            required
          >
            <option value="">Select a DC...</option>
            {pendingDcs.map((d) => (
              <option key={d.dc_no ?? d.sap_document_no} value={d.dc_no ?? ""}>
                {d.dc_no} — {d.vendor_name} ({d.material_code})
              </option>
            ))}
          </select>

          {selectedDispatch && (
            <p className="mb-3 text-xs text-gray-500">
              Expected: {selectedDispatch.quantity_front_case ?? 0} front +{" "}
              {selectedDispatch.quantity_back_case ?? 0} back ={" "}
              {(selectedDispatch.quantity_front_case ?? 0) +
                (selectedDispatch.quantity_back_case ?? 0)}{" "}
              total
            </p>
          )}

          <label className="mb-1 block text-sm font-medium text-gray-700">
            Actual Front Case Qty
          </label>
          <input
            type="number"
            className="mb-3 w-full rounded border px-3 py-2 text-sm"
            value={actualFrontCase}
            onChange={(e) => setActualFrontCase(e.target.value)}
            required
            min={0}
          />

          <label className="mb-1 block text-sm font-medium text-gray-700">
            Actual Back Case Qty
          </label>
          <input
            type="number"
            className="mb-4 w-full rounded border px-3 py-2 text-sm"
            value={actualBackCase}
            onChange={(e) => setActualBackCase(e.target.value)}
            required
            min={0}
          />

          {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {submitting ? "Verifying..." : "Verify"}
          </button>
        </form>
      )}

      {result && (
        <div
          className={`mt-4 max-w-md rounded border p-4 text-sm ${
            RESULT_STYLES[result.result] ?? ""
          }`}
        >
          <p className="mb-1 font-semibold">
            DC {result.dc_no} — {result.result.toUpperCase()}
          </p>
          <p>Expected: {result.expected_qty}, Actual: {result.actual_qty}</p>
          <p>Status: {result.verification_status}</p>
          {result.deviation_created && (
            <p className="mt-1 font-medium">
              A deviation record was created and the vendor has been notified.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

