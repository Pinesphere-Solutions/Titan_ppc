// M2 Dashboard — redesigned using the shared Card component and a
// consistent KPI card pattern. Data/logic unchanged: same
// /dashboard/summary fetch, same numbers.

import {
  AlertTriangle,
  ClipboardCheck,
  FileClock,
  GitBranch,
  Layers,
  Package,
  ShieldCheck,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";

interface DashboardSummary {
  total_dispatches: number;
  pending_verification: number;
  pending_qc_acknowledgement: number;
  open_deviations: number;
  total_movements_synced: number;
  open_po_count: number;
  total_pending_qty: number;
}

async function getDashboardSummary(): Promise<DashboardSummary> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL || "http://localhost:8000"; // server-side fetch — always call the local backend directly, never the public-facing (possibly relative) client base URL
  const res = await fetch(`${baseUrl}/dashboard/summary`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load dashboard summary (status ${res.status})`);
  }
  return res.json();
}

function KpiCard({
  label,
  value,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: number;
  icon: React.ElementType;
  tone?: "default" | "warning" | "error";
}) {
  const toneStyles = {
    default: { iconBg: "bg-primary-light", iconColor: "text-primary", value: "text-text-primary" },
    warning: { iconBg: "bg-warning-bg", iconColor: "text-warning", value: "text-warning-text" },
    error: { iconBg: "bg-error-bg", iconColor: "text-error", value: "text-error-text" },
  }[tone];

  return (
    <Card>
      <CardContent className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-secondary">{label}</p>
          <p className={`mt-1.5 text-2xl font-semibold ${toneStyles.value}`}>{value}</p>
        </div>
        <div className={`flex h-9 w-9 items-center justify-center rounded-md ${toneStyles.iconBg}`}>
          <Icon className={`h-4.5 w-4.5 ${toneStyles.iconColor}`} />
        </div>
      </CardContent>
    </Card>
  );
}

export default async function DashboardPage() {
  const summary = await getDashboardSummary();

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Live counts across the sub-con material tracking workflow."
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Total Dispatches" value={summary.total_dispatches} icon={Package} />
        <KpiCard
          label="Pending Verification"
          value={summary.pending_verification}
          icon={FileClock}
          tone={summary.pending_verification > 0 ? "warning" : "default"}
        />
        <KpiCard
          label="Pending QC Acknowledgement"
          value={summary.pending_qc_acknowledgement}
          icon={ClipboardCheck}
          tone={summary.pending_qc_acknowledgement > 0 ? "warning" : "default"}
        />
        <KpiCard
          label="Open Deviations"
          value={summary.open_deviations}
          icon={AlertTriangle}
          tone={summary.open_deviations > 0 ? "error" : "default"}
        />
        <KpiCard label="SAP Movements Synced" value={summary.total_movements_synced} icon={GitBranch} />
        <KpiCard label="Open Purchase Orders" value={summary.open_po_count} icon={ShieldCheck} />
        <KpiCard label="Total Pending PO Quantity" value={summary.total_pending_qty} icon={Layers} />
      </div>
    </div>
  );
}


