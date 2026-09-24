"use client";

// M7 Deviation Management
// Converted from a read-only server component to a client component,
// since resolving a deviation is an authenticated mutating action
// (same pattern as Masters). Resolving is a lightweight closure only —
// it does not reopen the underlying DeliveryChallan for re-verification.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

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
    <div>
      <PageHeader
        title="Deviation Management"
        description="Delivery challans where the received quantity was less than expected."
      />

      {error && <div className="mb-4"><ErrorState message={error} /></div>}

      {loading ? (
        <LoadingState label="Loading deviations..." />
      ) : deviations.length === 0 ? (
        <EmptyState
          title="No deviations recorded"
          description="Delivery challans with a quantity shortfall against SAP will appear here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>DC No</TableHeaderCell>
              <TableHeaderCell>Vendor</TableHeaderCell>
              <TableHeaderCell>Material</TableHeaderCell>
              <TableHeaderCell align="right">Expected</TableHeaderCell>
              <TableHeaderCell align="right">Actual</TableHeaderCell>
              <TableHeaderCell align="right">Difference</TableHeaderCell>
              <TableHeaderCell>Vendor Notified</TableHeaderCell>
              <TableHeaderCell>Vendor Status</TableHeaderCell>
              <TableHeaderCell></TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {deviations.map((d) => (
              <TableRow key={d.dc_no}>
                <TableCell>{d.dc_no}</TableCell>
                <TableCell>{d.vendor_name}</TableCell>
                <TableCell>{d.material_code}</TableCell>
                <TableCell align="right">{d.expected_qty}</TableCell>
                <TableCell align="right">{d.actual_qty}</TableCell>
                <TableCell align="right" className="font-medium text-error-text">
                  -{d.difference_qty}
                </TableCell>
                <TableCell>
                  <StatusBadge status={d.mail_status} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={d.vendor_status} />
                  {d.vendor_status === "resolved" && d.resolved_by && (
                    <p className="mt-0.5 text-xs text-text-muted">by {d.resolved_by}</p>
                  )}
                </TableCell>
                <TableCell align="right">
                  {d.vendor_status === "awaiting_response" && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResolve(d.dc_no)}
                      loading={resolvingDcNo === d.dc_no}
                    >
                      {resolvingDcNo === d.dc_no ? "Resolving..." : "Mark Resolved"}
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
