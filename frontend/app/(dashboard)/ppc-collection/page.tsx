"use client";

// M10 PPC Collection and Verification — the PPC team member collects
// material from the Sub-con Tray after UD Post (SAP 313) is done at M9,
// re-verifying it in the same action. This is what officially ends the
// Sub-con process per the KT notes (Module-Wireframe-Draft steps 39-42).

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";

interface PendingItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  model: string;
  quantity: number;
  ud_post_status: string;
}

interface CollectResult {
  dc_no: string;
  tray_no: string;
  vendor_name: string;
  verification_status: string;
  collected_by: string;
  message: string;
}

export default function PpcCollectionPage() {
  const [pendingDcs, setPendingDcs] = useState<PendingItem[]>([]);
  const [selectedDcNo, setSelectedDcNo] = useState("");
  const [trayNo, setTrayNo] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CollectResult | null>(null);

  async function loadPendingDcs() {
    setLoading(true);
    try {
      const res = await apiClient.get<PendingItem[]>("/ppc-collection/pending");
      setPendingDcs(res.data);
    } catch {
      setError("Failed to load delivery challans awaiting PPC collection.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingDcs();
  }, []);

  async function handleCollect() {
    if (!selectedDcNo) {
      setError("Select a delivery challan first.");
      return;
    }
    if (!trayNo.trim()) {
      setError("Enter the Sub-con Tray number.");
      return;
    }

    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await apiClient.post<CollectResult>(`/ppc-collection/${selectedDcNo}/collect`, {
        tray_no: trayNo.trim(),
      });
      setResult(res.data);
      setSelectedDcNo("");
      setTrayNo("");
      await loadPendingDcs();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Collection failed.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="PPC Collection & Verification"
        description="Collect material from the Sub-con Tray and confirm re-verification, ending the Sub-con process."
      />

      {loading ? (
        <LoadingState label="Loading delivery challans awaiting PPC collection..." />
      ) : pendingDcs.length === 0 ? (
        <EmptyState
          title="Nothing awaiting PPC collection"
          description="Delivery challans that have completed UD Post (SAP 313) and are waiting in the Sub-con Tray will appear here."
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

            <Input
              label="Sub-con Tray No"
              placeholder="e.g. TRAY-014"
              value={trayNo}
              onChange={(e) => setTrayNo(e.target.value)}
            />

            {error && <ErrorState message={error} />}

            <Button
              onClick={handleCollect}
              loading={submitting}
              disabled={!selectedDcNo || !trayNo.trim()}
              className="w-full"
            >
              {submitting ? "Confirming Collection..." : "Confirm Collection & Verification"}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-4 max-w-md rounded-lg border border-success-bg bg-success-bg p-5 shadow-sm">
          <p className="mb-1 text-sm font-semibold text-success-text">{result.message}</p>
          <p className="text-sm text-success-text">Collected by: {result.collected_by}</p>
        </div>
      )}
    </div>
  );
}
