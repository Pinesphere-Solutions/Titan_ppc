// M9 SAP Processing
// Server component — read-only list of movement records (101/313/321),
// same pattern as M3 SAP Material Outward and M7 Deviation Management.

import { PageHeader } from "@/components/ui/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

interface MovementItem {
  material_document_no: string;
  movement_type: string;
  dc_no: string;
  posting_date: string | null;
  sync_status: string;
}

const MOVEMENT_TYPE_LABELS: Record<string, string> = {
  "101": "101 — Goods Receipt",
  "313": "313 — Stock Transfer",
  "321": "321 — Quality to Unrestricted",
};

const MOVEMENT_TYPE_VARIANT: Record<string, "info" | "warning" | "success"> = {
  "101": "info",
  "313": "warning",
  "321": "success",
};

async function getMovements(): Promise<MovementItem[]> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL || "http://localhost:8000"; // server-side fetch — always call the local backend directly, never the public-facing (possibly relative) client base URL

  const res = await fetch(`${baseUrl}/sap-processing/list`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to load movements (status ${res.status})`);
  }

  return res.json();
}

export default async function SapProcessingPage() {
  const movements = await getMovements();

  return (
    <div>
      <PageHeader
        title="SAP Processing"
        description="Movement records synced from SAP: goods receipt, stock transfer, and quality to unrestricted stock."
      />

      {movements.length === 0 ? (
        <EmptyState
          title="No movement records synced yet"
          description="Goods receipt, stock transfer, and quality-to-unrestricted movements will appear here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Material Document No</TableHeaderCell>
              <TableHeaderCell>Movement Type</TableHeaderCell>
              <TableHeaderCell>DC No</TableHeaderCell>
              <TableHeaderCell>Posting Date</TableHeaderCell>
              <TableHeaderCell>Sync Status</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {movements.map((m) => (
              <TableRow key={m.material_document_no}>
                <TableCell className="font-mono text-xs">{m.material_document_no}</TableCell>
                <TableCell>
                  <Badge variant={MOVEMENT_TYPE_VARIANT[m.movement_type] ?? "neutral"}>
                    {MOVEMENT_TYPE_LABELS[m.movement_type] ?? m.movement_type}
                  </Badge>
                </TableCell>
                <TableCell>{m.dc_no}</TableCell>
                <TableCell>{m.posting_date ?? "—"}</TableCell>
                <TableCell className="text-xs text-text-secondary">{m.sync_status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
