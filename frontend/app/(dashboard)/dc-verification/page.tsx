"use client";

// M5 DC Verification
// Client component — needs interactivity (form submission, live result
// display) unlike the read-only M3 screen. Fetches the pending DC list
// from the existing /sap-outward/list endpoint (M3's endpoint), filtered
// client-side to status === "pending", rather than building a second
// backend endpoint just for this dropdown.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";

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

const RESULT_VARIANT: Record<string, "success" | "info" | "error"> = {
  matched: "success",
  excess: "info",
  less: "error",
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
    <div>
      <PageHeader
        title="DC Verification"
        description="Compare physically received quantity against the expected quantity from SAP."
      />

      {loading ? (
        <LoadingState label="Loading pending delivery challans..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing pending verification"
          description="Delivery challans dispatched from SAP will appear here once they need verification."
        />
      ) : (
        <Card className="max-w-md">
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Select
                label="Delivery Challan"
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
              </Select>

              {selectedDispatch && (
                <p className="text-xs text-text-secondary">
                  Expected: {selectedDispatch.quantity_front_case ?? 0} front +{" "}
                  {selectedDispatch.quantity_back_case ?? 0} back ={" "}
                  {(selectedDispatch.quantity_front_case ?? 0) +
                    (selectedDispatch.quantity_back_case ?? 0)}{" "}
                  total
                </p>
              )}

              <Input
                label="Actual Front Case Qty"
                type="number"
                value={actualFrontCase}
                onChange={(e) => setActualFrontCase(e.target.value)}
                required
                min={0}
              />

              <Input
                label="Actual Back Case Qty"
                type="number"
                value={actualBackCase}
                onChange={(e) => setActualBackCase(e.target.value)}
                required
                min={0}
              />

              {error && <ErrorState message={error} />}

              <Button type="submit" loading={submitting} className="w-full">
                {submitting ? "Verifying..." : "Verify"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className="mt-4 max-w-md">
          <CardContent className="space-y-1.5">
            <div className="flex items-center gap-2">
              <p className="text-sm font-semibold text-text-primary">DC {result.dc_no}</p>
              <Badge variant={RESULT_VARIANT[result.result] ?? "neutral"}>
                {result.result.toUpperCase()}
              </Badge>
            </div>
            <p className="text-sm text-text-secondary">
              Expected: {result.expected_qty}, Actual: {result.actual_qty}
            </p>
            <p className="text-sm text-text-secondary">Status: {result.verification_status}</p>
            {result.deviation_created && (
              <p className="mt-1 text-sm font-medium text-text-primary">
                A deviation record was created and the vendor has been notified.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
