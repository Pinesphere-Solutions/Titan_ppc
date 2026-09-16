"use client";

// M8 QC Acknowledgement
// Same pattern as M5 DC Verification: fetch the existing /sap-outward/list
// endpoint, filter client-side to DCs that are verified but not yet QC
// acknowledged, and offer a single-action button rather than a form,
// since acknowledgement has no quantity input — it's a confirmation.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface DispatchListItem {
  sap_document_no: string;
  dc_no: string | null;
  vendor_name: string;
  material_code: string;
  verification_status: string | null;
  qc_ack_status: string | null;
  stock_level: string | null;
}

interface AcknowledgeResult {
  dc_no: string;
  qc_ack_status: string;
  qc_acknowledged_by: string | null;
  stock_level: string;
  ud_post_status: string;
}

export default function QcAcknowledgementPage() {
  const [eligibleDcs, setEligibleDcs] = useState<DispatchListItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AcknowledgeResult | null>(null);

  async function loadEligibleDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<DispatchListItem[]>("/sap-outward/list");
      setEligibleDcs(
        res.data.filter(
          (item) => item.verification_status === "verified" && item.qc_ack_status === "pending"
        )
      );
    } catch {
      setError("Failed to load delivery challans awaiting acknowledgement.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadEligibleDcs();
  }, []);

  async function handleAcknowledge() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<AcknowledgeResult>(
        `/qc-acknowledgement/${selectedDcNo}/acknowledge`
      );
      setResult(res.data);
      setSelectedDcNo("");
      await loadEligibleDcs(); // acknowledged DC drops out of the list
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Acknowledgement failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M8 — QC Acknowledgement</h1>
      <p className="mb-4 text-sm text-gray-500">
        Confirm QC has accepted a verified delivery challan. This moves stock from
        Level 2 to Level 1 and triggers the UD Post to SAP.
      </p>

      {loading ? (
        <p className="text-sm text-gray-500">Loading delivery challans awaiting acknowledgement...</p>
      ) : eligibleDcs.length === 0 ? (
        <p className="text-sm text-gray-500">
          No verified delivery challans are currently awaiting QC acknowledgement.
        </p>
      ) : (
        <div className="max-w-md rounded border p-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Delivery Challan
          </label>
          <select
            className="mb-4 w-full rounded border px-3 py-2 text-sm"
            value={selectedDcNo}
            onChange={(e) => setSelectedDcNo(e.target.value)}
          >
            <option value="">Select a DC...</option>
            {eligibleDcs.map((d) => (
              <option key={d.dc_no ?? d.sap_document_no} value={d.dc_no ?? ""}>
                {d.dc_no} — {d.vendor_name} ({d.material_code})
              </option>
            ))}
          </select>

          {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

          <button
            onClick={handleAcknowledge}
            disabled={submitting || !selectedDcNo}
            className="w-full rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {submitting ? "Acknowledging..." : "Acknowledge"}
          </button>
        </div>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded border border-green-300 bg-green-100 p-4 text-sm text-green-800">
          <p className="mb-1 font-semibold">DC {result.dc_no} acknowledged</p>
          <p>Acknowledged by: {result.qc_acknowledged_by}</p>
          <p>Stock level: {result.stock_level}</p>
          <p>UD Post status: {result.ud_post_status}</p>
        </div>
      )}
    </div>
  );
}