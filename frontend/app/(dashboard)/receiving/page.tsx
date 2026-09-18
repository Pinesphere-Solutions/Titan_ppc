"use client";

// M4 Material Receiving — categorizes a DC as Regular or Rework once
// it has been received at sub-con (see the Sub-con Scan kiosk).
// Additive/informational: does not gate DC Verification. See the
// DeliveryChallan model's White Box simplification note for the known
// gap between this DC-centric build and the original per-box KT design.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";

interface ReceivingListItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  receiving_category: string | null;
}

interface CategorizeResult {
  dc_no: string;
  vendor_name: string;
  receiving_category: string;
  message: string;
}

export default function MaterialReceivingPage() {
  const [pendingDcs, setPendingDcs] = useState<ReceivingListItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [category, setCategory] = useState("regular");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CategorizeResult | null>(null);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<ReceivingListItem[]>("/receiving/pending-categorization");
      setPendingDcs(res.data);
    } catch {
      setError("Failed to load delivery challans awaiting categorization.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
  }, []);

  async function handleCategorize() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<CategorizeResult>(`/receiving/${selectedDcNo}/categorize`, {
        category,
      });
      setResult(res.data);
      setSelectedDcNo("");
      await loadPendingDcs();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Categorization failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Material Receiving"
        description="Categorize a delivery challan as Regular or Rework once it has been received at sub-con."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting categorization..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting categorization"
          description="Delivery challans received at sub-con but not yet categorized will appear here."
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

            <Select
              label="Receiving Category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="regular">Regular</option>
              <option value="rework">Rework</option>
            </Select>

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleCategorize}
              loading={submitting}
              disabled={!selectedDcNo}
              className="w-full"
            >
              {submitting ? "Saving..." : "Save Category"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded-lg border border-success-bg bg-success-bg p-5 shadow-sm">
          <p className="mb-1 text-sm font-semibold text-success-text">{result.message}</p>
          <p className="text-sm text-success-text">Vendor: {result.vendor_name}</p>
          <p className="text-sm text-success-text">Category: {result.receiving_category}</p>
        </div>
      )}
    </div>
  );
}
