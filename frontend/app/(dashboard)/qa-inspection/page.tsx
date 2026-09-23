"use client";

// M11 QA Inspection — a separate Quality Team inspects material after
// PPC Collection (M10) ends the Sub-con process. A DC starts out
// "waiting_for_inspection" (implicit — no queue action needed), moves
// to "in_progress" once someone starts it, and "completed" once done.
// Completed items drop off this queue; the next stop is ZQMTL1 (M12).

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@/components/ui/Table";

interface QueueItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  model: string;
  inspection_status: string;
  qa_user: string | null;
}

export default function QaInspectionPage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actingOn, setActingOn] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadQueue() {
    setLoading(true);
    try {
      const res = await apiClient.get<QueueItem[]>("/qa-inspection/queue");
      setQueue(res.data);
    } catch {
      setError("Failed to load the QA inspection queue.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadQueue();
  }, []);

  async function handleStart(dcNo: string) {
    setError(null);
    setActingOn(dcNo);
    try {
      await apiClient.post(`/qa-inspection/${dcNo}/start`);
      await loadQueue();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to start inspection.";
      setError(message);
    } finally {
      setActingOn(null);
    }
  }

  async function handleComplete(dcNo: string) {
    setError(null);
    setActingOn(dcNo);
    try {
      await apiClient.post(`/qa-inspection/${dcNo}/complete`);
      await loadQueue();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to complete inspection.";
      setError(message);
    } finally {
      setActingOn(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="QA Inspection"
        description="Quality Team inspection queue — material collected by PPC waits here until inspection is started and completed."
      />

      {error && <div className="mb-4"><ErrorState message={error} /></div>}

      {loading ? (
        <LoadingState label="Loading the QA inspection queue..." />
      ) : queue.length === 0 ? (
        <EmptyState
          title="Nothing waiting for inspection"
          description="Material collected by PPC that still needs Quality Team inspection will appear here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>DC No</TableHeaderCell>
              <TableHeaderCell>Vendor</TableHeaderCell>
              <TableHeaderCell>Material</TableHeaderCell>
              <TableHeaderCell>Model</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>QA User</TableHeaderCell>
              <TableHeaderCell align="right">Action</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {queue.map((item) => (
              <TableRow key={item.dc_no}>
                <TableCell>{item.dc_no}</TableCell>
                <TableCell>{item.vendor_name}</TableCell>
                <TableCell>{item.material_code}</TableCell>
                <TableCell>{item.model}</TableCell>
                <TableCell>
                  <StatusBadge status={item.inspection_status} />
                </TableCell>
                <TableCell>{item.qa_user ?? "—"}</TableCell>
                <TableCell align="right">
                  {item.inspection_status === "waiting_for_inspection" ? (
                    <Button
                      size="sm"
                      loading={actingOn === item.dc_no}
                      onClick={() => handleStart(item.dc_no)}
                    >
                      Start Inspection
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      loading={actingOn === item.dc_no}
                      onClick={() => handleComplete(item.dc_no)}
                    >
                      Complete Inspection
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
