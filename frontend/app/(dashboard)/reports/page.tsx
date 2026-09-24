"use client";

// M14 Reports — Material Movement History (the original timeline view)
// plus the 5 report types from the KT notes: Vendor, QC, SAP, Deviation,
// and Storage reports. Converted from a server component to a client
// component so all 6 can share one page with tab switching, fetched via
// apiClient rather than a server-side fetch per report.

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

interface MovementHistoryEvent {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  event_type: string;
  description: string;
  quantity: number | null;
  event_date: string;
}

interface VendorReportItem {
  vendor_code: string;
  vendor_name: string;
  total_dispatches: number;
  total_dcs: number;
  pending_qc: number;
  total_deviations: number;
}

interface QcReportItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  qc_ack_status: string;
  qc_acknowledged_by: string | null;
  qc_acknowledged_at: string | null;
  stock_level: string;
}

interface SapReportItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  material_document_no: string;
  movement_type: string;
  movement_label: string;
  posting_date: string | null;
  sync_status: string;
}

interface DeviationReportItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  deviation_type: string;
  expected_qty: number;
  actual_qty: number;
  difference_qty: number;
  mail_status: string;
  vendor_status: string;
  created_at: string;
}

interface StorageReportItem {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  rack: string;
  row: string;
  bin: string;
  storage_location: string;
  stored_by: string;
  stored_at: string;
}

const TABS = [
  { key: "movement", label: "Material Movement" },
  { key: "vendor", label: "Vendor Report" },
  { key: "qc", label: "QC Report" },
  { key: "sap", label: "SAP Report" },
  { key: "deviation", label: "Deviation Report" },
  { key: "storage", label: "Storage Report" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const EVENT_VARIANT: Record<string, "info" | "success" | "neutral"> = {
  received: "info",
  qc_acknowledged: "success",
  sap_movement: "neutral",
};

const EVENT_LABELS: Record<string, string> = {
  received: "Received",
  qc_acknowledged: "QC Acknowledged",
  sap_movement: "SAP Movement",
};

function formatEventDate(raw: string): string {
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
}

function formatDate(raw: string | null): string {
  if (!raw) return "—";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function MovementHistoryView({ events }: { events: MovementHistoryEvent[] }) {
  const grouped = events.reduce<Record<string, MovementHistoryEvent[]>>((acc, e) => {
    (acc[e.dc_no] ??= []).push(e);
    return acc;
  }, {});

  if (Object.keys(grouped).length === 0) {
    return (
      <EmptyState
        title="No movement history yet"
        description="History will appear here once delivery challans are received and processed."
      />
    );
  }

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([dcNo, dcEvents]) => (
        <Card key={dcNo} className="max-w-3xl">
          <CardHeader className="flex flex-row items-baseline justify-between">
            <CardTitle>{dcNo}</CardTitle>
            <span className="text-xs text-text-secondary">
              {dcEvents[0].vendor_name} · {dcEvents[0].material_code}
            </span>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3 border-l-2 border-border pl-4">
              {dcEvents.map((e, i) => (
                <li key={i} className="text-sm">
                  <div className="flex items-center gap-2">
                    <Badge variant={EVENT_VARIANT[e.event_type] ?? "neutral"}>
                      {EVENT_LABELS[e.event_type] ?? e.event_type}
                    </Badge>
                    <span className="text-xs text-text-muted">{formatEventDate(e.event_date)}</span>
                  </div>
                  <p className="mt-1 text-text-primary">
                    {e.description}
                    {e.quantity !== null && <span className="text-text-secondary"> — qty {e.quantity}</span>}
                  </p>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function VendorReportView({ rows }: { rows: VendorReportItem[] }) {
  if (rows.length === 0) return <EmptyState title="No vendor activity yet" />;
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>Vendor Code</TableHeaderCell>
          <TableHeaderCell>Vendor Name</TableHeaderCell>
          <TableHeaderCell align="right">Dispatches</TableHeaderCell>
          <TableHeaderCell align="right">DCs</TableHeaderCell>
          <TableHeaderCell align="right">Pending QC</TableHeaderCell>
          <TableHeaderCell align="right">Deviations</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.vendor_code}>
            <TableCell className="font-mono text-xs">{r.vendor_code}</TableCell>
            <TableCell>{r.vendor_name}</TableCell>
            <TableCell align="right">{r.total_dispatches}</TableCell>
            <TableCell align="right">{r.total_dcs}</TableCell>
            <TableCell align="right">{r.pending_qc}</TableCell>
            <TableCell align="right">{r.total_deviations}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function QcReportView({ rows }: { rows: QcReportItem[] }) {
  if (rows.length === 0) return <EmptyState title="No QC records yet" />;
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>DC No</TableHeaderCell>
          <TableHeaderCell>Vendor</TableHeaderCell>
          <TableHeaderCell>Material</TableHeaderCell>
          <TableHeaderCell>QC Status</TableHeaderCell>
          <TableHeaderCell>Acknowledged By</TableHeaderCell>
          <TableHeaderCell>Date</TableHeaderCell>
          <TableHeaderCell>Stock Level</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.dc_no}>
            <TableCell className="font-mono text-xs">{r.dc_no}</TableCell>
            <TableCell>{r.vendor_name}</TableCell>
            <TableCell>{r.material_code}</TableCell>
            <TableCell><StatusBadge status={r.qc_ack_status} /></TableCell>
            <TableCell>{r.qc_acknowledged_by ?? "—"}</TableCell>
            <TableCell>{formatDate(r.qc_acknowledged_at)}</TableCell>
            <TableCell>{r.stock_level}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function SapReportView({ rows }: { rows: SapReportItem[] }) {
  if (rows.length === 0) return <EmptyState title="No SAP postings yet" />;
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>DC No</TableHeaderCell>
          <TableHeaderCell>Vendor</TableHeaderCell>
          <TableHeaderCell>Material</TableHeaderCell>
          <TableHeaderCell>Material Doc No</TableHeaderCell>
          <TableHeaderCell>Movement</TableHeaderCell>
          <TableHeaderCell>Posting Date</TableHeaderCell>
          <TableHeaderCell>Sync Status</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.material_document_no}>
            <TableCell className="font-mono text-xs">{r.dc_no}</TableCell>
            <TableCell>{r.vendor_name}</TableCell>
            <TableCell>{r.material_code}</TableCell>
            <TableCell className="font-mono text-xs">{r.material_document_no}</TableCell>
            <TableCell>{r.movement_type} — {r.movement_label}</TableCell>
            <TableCell>{r.posting_date ?? "—"}</TableCell>
            <TableCell><StatusBadge status={r.sync_status} /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function DeviationReportView({ rows }: { rows: DeviationReportItem[] }) {
  if (rows.length === 0) return <EmptyState title="No deviations recorded yet" />;
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>DC No</TableHeaderCell>
          <TableHeaderCell>Vendor</TableHeaderCell>
          <TableHeaderCell>Material</TableHeaderCell>
          <TableHeaderCell>Type</TableHeaderCell>
          <TableHeaderCell align="right">Expected</TableHeaderCell>
          <TableHeaderCell align="right">Actual</TableHeaderCell>
          <TableHeaderCell align="right">Diff</TableHeaderCell>
          <TableHeaderCell>Mail Status</TableHeaderCell>
          <TableHeaderCell>Vendor Status</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((r, i) => (
          <TableRow key={`${r.dc_no}-${i}`}>
            <TableCell className="font-mono text-xs">{r.dc_no}</TableCell>
            <TableCell>{r.vendor_name}</TableCell>
            <TableCell>{r.material_code}</TableCell>
            <TableCell>{r.deviation_type}</TableCell>
            <TableCell align="right">{r.expected_qty}</TableCell>
            <TableCell align="right">{r.actual_qty}</TableCell>
            <TableCell align="right">{r.difference_qty}</TableCell>
            <TableCell><StatusBadge status={r.mail_status} /></TableCell>
            <TableCell><StatusBadge status={r.vendor_status} /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function StorageReportView({ rows }: { rows: StorageReportItem[] }) {
  if (rows.length === 0) return <EmptyState title="No stored items yet" />;
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>DC No</TableHeaderCell>
          <TableHeaderCell>Vendor</TableHeaderCell>
          <TableHeaderCell>Material</TableHeaderCell>
          <TableHeaderCell>Rack</TableHeaderCell>
          <TableHeaderCell>Row</TableHeaderCell>
          <TableHeaderCell>Bin</TableHeaderCell>
          <TableHeaderCell>Location</TableHeaderCell>
          <TableHeaderCell>Stored By</TableHeaderCell>
          <TableHeaderCell>Stored Date</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((r, i) => (
          <TableRow key={`${r.dc_no}-${i}`}>
            <TableCell className="font-mono text-xs">{r.dc_no}</TableCell>
            <TableCell>{r.vendor_name}</TableCell>
            <TableCell>{r.material_code}</TableCell>
            <TableCell>{r.rack}</TableCell>
            <TableCell>{r.row}</TableCell>
            <TableCell>{r.bin}</TableCell>
            <TableCell>{r.storage_location}</TableCell>
            <TableCell>{r.stored_by}</TableCell>
            <TableCell>{formatDate(r.stored_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("movement");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [movementEvents, setMovementEvents] = useState<MovementHistoryEvent[]>([]);
  const [vendorRows, setVendorRows] = useState<VendorReportItem[]>([]);
  const [qcRows, setQcRows] = useState<QcReportItem[]>([]);
  const [sapRows, setSapRows] = useState<SapReportItem[]>([]);
  const [deviationRows, setDeviationRows] = useState<DeviationReportItem[]>([]);
  const [storageRows, setStorageRows] = useState<StorageReportItem[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        switch (activeTab) {
          case "movement": {
            const res = await apiClient.get<MovementHistoryEvent[]>("/reports/material-movement-history");
            if (!cancelled) setMovementEvents(res.data);
            break;
          }
          case "vendor": {
            const res = await apiClient.get<VendorReportItem[]>("/reports/vendor-report");
            if (!cancelled) setVendorRows(res.data);
            break;
          }
          case "qc": {
            const res = await apiClient.get<QcReportItem[]>("/reports/qc-report");
            if (!cancelled) setQcRows(res.data);
            break;
          }
          case "sap": {
            const res = await apiClient.get<SapReportItem[]>("/reports/sap-report");
            if (!cancelled) setSapRows(res.data);
            break;
          }
          case "deviation": {
            const res = await apiClient.get<DeviationReportItem[]>("/reports/deviation-report");
            if (!cancelled) setDeviationRows(res.data);
            break;
          }
          case "storage": {
            const res = await apiClient.get<StorageReportItem[]>("/reports/storage-report");
            if (!cancelled) setStorageRows(res.data);
            break;
          }
        }
      } catch {
        if (!cancelled) setError("Failed to load this report.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [activeTab]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Reports"
        description="Inward, vendor, QC, SAP, deviation and storage reports across the material tracking flow."
      />

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-primary text-white"
                : "text-text-secondary hover:bg-surface hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {error && <ErrorState message={error} />}

      {loading ? (
        <LoadingState label="Loading report..." />
      ) : activeTab === "movement" ? (
        <MovementHistoryView events={movementEvents} />
      ) : (
        <Card>
          <CardContent>
            {activeTab === "vendor" && <VendorReportView rows={vendorRows} />}
            {activeTab === "qc" && <QcReportView rows={qcRows} />}
            {activeTab === "sap" && <SapReportView rows={sapRows} />}
            {activeTab === "deviation" && <DeviationReportView rows={deviationRows} />}
            {activeTab === "storage" && <StorageReportView rows={storageRows} />}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
