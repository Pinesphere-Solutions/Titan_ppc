"use client";

// M12 ZQMTL1 Processing — once QA Inspection (M11) is complete, this
// screen performs the material check, UD Post, and move to SAP 313 for
// Level 1 (ZQMTL1) as one combined confirm action.

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
  model: string;
  quantity: number;
}

interface ProcessResult {
  dc_no: string;
  vendor_name: string;
  zqmtl1_status: string;
  sap_status: string;
  processed_by: string;
  message: string;
}

export default function Zqmtl1Page() {
  const [pendingDcs, setPendingDcs] = useState<PendingItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessResult | null>(null);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<PendingItem[]>("/zqmtl1/pending");
      setPendingDcs(res.data);
    } catch {
      setError("Failed to load delivery challans awaiting ZQMTL1 processing.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
  }, []);

  async function handleProcess() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<ProcessResult>(`/zqmtl1/${selectedDcNo}/process`);
      setResult(res.data);
      setSelectedDcNo("");
      await loadPendingDcs();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Processing failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="ZQMTL1 Processing"
        description="Material check, UD Post, and move to SAP 313 for material that has cleared QA Inspection."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting ZQMTL1 processing..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting ZQMTL1 processing"
          description="Delivery challans that have completed QA Inspection will appear here."
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
                  {d.dc_no} — {d.vendor_name} ({d.material_code}, {d.model}, qty {d.quantity})
                </option>
              ))}
            </Select>

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleProcess}
              loading={submitting}
              disabled={!selectedDcNo}
              className="w-full"
            >
              {submitting ? "Processing..." : "Process at ZQMTL1"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded-lg border border-success-bg bg-success-bg p-5 shadow-sm">
          <p className="mb-1 text-sm font-semibold text-success-text">{result.message}</p>
          <p className="text-sm text-success-text">Processed by: {result.processed_by}</p>
        </div>
      )}
    </div>
  );
}
