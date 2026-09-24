// M3 SAP Material Outward
// Server component — fetches directly from the backend on each request,
// per architecture doc Section 5.1 ("server components for read-heavy
// screens such as dashboard, reports, masters"). No client-side state
// needed for a plain read-only list like this.

import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/States";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeaderCell,
  TableCell,
} from "@/components/ui/Table";

interface DispatchListItem {
  sap_document_no: string;
  dc_no: string | null;
  vendor_name: string;
  material_code: string;
  model: string | null;
  quantity_front_case: number | null;
  quantity_back_case: number | null;
  dispatch_date: string | null;
  verification_status: string | null;
}

async function getDispatchedMaterials(): Promise<DispatchListItem[]> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL || "http://localhost:8000"; // server-side fetch — always call the local backend directly, never the public-facing (possibly relative) client base URL

  const res = await fetch(`${baseUrl}/sap-outward/list`, {
    cache: "no-store", // always fresh — this data changes on every sync/verify
  });

  if (!res.ok) {
    throw new Error(`Failed to load dispatched materials (status ${res.status})`);
  }

  return res.json();
}

export default async function SAPMaterialOutwardPage() {
  const items = await getDispatchedMaterials();

  return (
    <div>
      <PageHeader
        title="SAP Material Outward"
        description="Materials dispatched from Titan to vendors."
      />

      {items.length === 0 ? (
        <EmptyState
          title="No dispatched materials yet"
          description="Materials synced from SAP will appear here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>SAP Doc No</TableHeaderCell>
              <TableHeaderCell>DC No</TableHeaderCell>
              <TableHeaderCell>Vendor</TableHeaderCell>
              <TableHeaderCell>Material</TableHeaderCell>
              <TableHeaderCell>Model</TableHeaderCell>
              <TableHeaderCell align="right">Front Qty</TableHeaderCell>
              <TableHeaderCell align="right">Back Qty</TableHeaderCell>
              <TableHeaderCell>Dispatch Date</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.sap_document_no}>
                <TableCell className="font-mono text-xs">{item.sap_document_no}</TableCell>
                <TableCell>{item.dc_no ?? "—"}</TableCell>
                <TableCell>{item.vendor_name}</TableCell>
                <TableCell>{item.material_code}</TableCell>
                <TableCell>{item.model ?? "—"}</TableCell>
                <TableCell align="right">{item.quantity_front_case ?? "—"}</TableCell>
                <TableCell align="right">{item.quantity_back_case ?? "—"}</TableCell>
                <TableCell>{item.dispatch_date ?? "—"}</TableCell>
                <TableCell>
                  <StatusBadge status={item.verification_status ?? "pending"} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
