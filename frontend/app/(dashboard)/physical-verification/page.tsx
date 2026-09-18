"use client";

// M6 Physical Verification — a confirmation checkpoint after DC
// Verification (M5), per the KT process's documented sequence. Does
// NOT gate QC Acknowledgement (M8) — see the service layer's docstring
// for why this is deliberately additive rather than a hard prerequisite.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";

interface PendingItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  verification_status: string;
  physical_verification_status: string;
}

interface ConfirmResult {
  dc_no: string;
  vendor_name: string;
  physical_verification_status: string;
  verified_by: string;
  message: string;
}

export default function PhysicalVerificationPage() {
  const [pendingDcs, setPendingDcs] = useState<PendingItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ConfirmResult | null>(null);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<PendingItem[]>("/physical-verification/pending");
      setPendingDcs(res.data);
    } catch {
      setError("Failed to load delivery challans awaiting physical verification.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
  }, []);

  async function handleConfirm() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<ConfirmResult>(`/physical-verification/${selectedDcNo}/confirm`);
      setResult(res.data);
      setSelectedDcNo("");
      await loadPendingDcs();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Confirmation failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Physical Verification"
        description="Confirm the physically received material matches what was verified against SAP."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting physical verification..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting physical verification"
          description="Verified delivery challans that still need a physical confirmation will appear here."
        />
      ) : (
        <Card className="max-w-md">
          <CardContent className="space-y-4">
            <Select
              label="Delivery Challan"
              value={selectedDcNo}
              onChange={(e) => setSelectedDcNo(e.target.value)}
            >
              <option value="">Select a DC...</option>
              {pendingDcs.map((d) => (
                <option key={d.dc_no} value={d.dc_no}>
                  {d.dc_no} — {d.vendor_name} ({d.material_code})
                </option>
              ))}
            </Select>

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleConfirm}
              loading={submitting}
              disabled={!selectedDcNo}
              className="w-full"
            >
              {submitting ? "Confirming..." : "Confirm Physical Verification"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded-lg border border-success-bg bg-success-bg p-5 shadow-sm">
          <p className="mb-1 text-sm font-semibold text-success-text">{result.message}</p>
          <p className="text-sm text-success-text">Verified by: {result.verified_by}</p>
        </div>
      )}
    </div>
  );
}

