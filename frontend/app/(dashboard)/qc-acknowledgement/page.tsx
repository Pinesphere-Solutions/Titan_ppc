"use client";

// M8 QC Acknowledgement
// Same pattern as M5 DC Verification: fetch the existing /sap-outward/list
// endpoint, filter client-side to DCs that are verified but not yet QC
// acknowledged, and offer a single-action button rather than a form,
// since acknowledgement has no quantity input — it's a confirmation.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";

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
    <div>
      <PageHeader
        title="QC Acknowledgement"
        description="Confirm QC has accepted a verified delivery challan. This moves stock from Level 2 to Level 1 and triggers the UD Post to SAP."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting acknowledgement..." />
      ) : eligibleDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting acknowledgement"
          description="Verified delivery challans awaiting QC acknowledgement will appear here."
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
              {eligibleDcs.map((d) => (
                <option key={d.dc_no ?? d.sap_document_no} value={d.dc_no ?? ""}>
                  {d.dc_no} — {d.vendor_name} ({d.material_code})
                </option>
              ))}
            </Select>

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleAcknowledge}
              loading={submitting}
              disabled={!selectedDcNo}
              className="w-full"
            >
              {submitting ? "Acknowledging..." : "Acknowledge"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className="mt-4 max-w-md">
          <CardContent className="space-y-1.5">
            <p className="text-sm font-semibold text-success-text">DC {result.dc_no} acknowledged</p>
            <p className="text-sm text-text-secondary">Acknowledged by: {result.qc_acknowledged_by}</p>
            <p className="text-sm text-text-secondary">Stock level: {result.stock_level}</p>
            <p className="text-sm text-text-secondary">UD Post status: {result.ud_post_status}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
