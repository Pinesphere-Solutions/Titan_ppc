"use client";

// M7 Deviation Management
// Converted from a read-only server component to a client component,
// since resolving a deviation is an authenticated mutating action
// (same pattern as Masters). Resolving is a lightweight closure only —
// it does not reopen the underlying DeliveryChallan for re-verification.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

interface DeviationItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  deviation_type: string;
  expected_qty: number;
  actual_qty: number;
  difference_qty: number;
  mail_status: string;
  vendor_status: string;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
}

const MAIL_STATUS_STYLES: Record<string, string> = {
  sent: "bg-green-100 text-green-800",
  pending: "bg-gray-100 text-gray-700",
  no_email_on_file: "bg-amber-100 text-amber-800",
};

const VENDOR_STATUS_STYLES: Record<string, string> = {
  awaiting_response: "bg-amber-100 text-amber-800",
  resolved: "bg-green-100 text-green-800",
};

export default function DeviationManagementPage() {
  const [deviations, setDeviations] = useState<DeviationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingDcNo, setResolvingDcNo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadDeviations() {
    setLoading(true);
    try {
      const res = await apiClient.get<DeviationItem[]>("/deviations/list");
      setDeviations(res.data);
    } catch {
      setError("Failed to load deviations.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDeviations();
  }, []);

  async function handleResolve(dcNo: string) {
    setError(null);
    setResolvingDcNo(dcNo);
    try {
      await apiClient.post(`/deviations/${dcNo}/resolve`);
      await loadDeviations();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to resolve deviation.";
      setError(message);
    } finally {
      setResolvingDcNo(null);
    }
  }

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M7 — Deviation Management</h1>
      <p className="mb-4 text-sm text-gray-500">
        Delivery challans where the received quantity was less than expected.
      </p>

      {loading ? (
        <p className="text-sm text-gray-500">Loading deviations...</p>
      ) : deviations.length === 0 ? (
        <p className="text-sm text-gray-500">No deviations recorded yet.</p>
      ) : (
        <div className="overflow-x-auto rounded border">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-600">DC No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Material</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Expected</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Actual</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Difference</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor Notified</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor Status</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {deviations.map((d) => (
                <tr key={d.dc_no}>
                  <td className="px-4 py-2">{d.dc_no}</td>
                  <td className="px-4 py-2">{d.vendor_name}</td>
                  <td className="px-4 py-2">{d.material_code}</td>
                  <td className="px-4 py-2 text-right">{d.expected_qty}</td>
                  <td className="px-4 py-2 text-right">{d.actual_qty}</td>
                  <td className="px-4 py-2 text-right font-medium text-red-700">
                    -{d.difference_qty}
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        MAIL_STATUS_STYLES[d.mail_status] ?? MAIL_STATUS_STYLES.pending
                      }`}
                    >
                      {d.mail_status}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        VENDOR_STATUS_STYLES[d.vendor_status] ?? "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {d.vendor_status}
                    </span>
                    {d.vendor_status === "resolved" && d.resolved_by && (
                      <p className="mt-0.5 text-xs text-gray-400">
                        by {d.resolved_by}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {d.vendor_status === "awaiting_response" && (
                      <button
                        onClick={() => handleResolve(d.dc_no)}
                        disabled={resolvingDcNo === d.dc_no}
                        className="rounded border px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                      >
                        {resolvingDcNo === d.dc_no ? "Resolving..." : "Mark Resolved"}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}



