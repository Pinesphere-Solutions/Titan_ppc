// M3 SAP Material Outward
// Server component — fetches directly from the backend on each request,
// per architecture doc Section 5.1 ("server components for read-heavy
// screens such as dashboard, reports, masters"). No client-side state
// needed for a plain read-only list like this.

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

const STATUS_STYLES: Record<string, string> = {
  verified: "bg-green-100 text-green-800",
  reverted: "bg-red-100 text-red-800",
  pending: "bg-gray-100 text-gray-700",
};

async function getDispatchedMaterials(): Promise<DispatchListItem[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M3 — SAP Material Outward</h1>
      <p className="mb-4 text-sm text-gray-500">
        Materials dispatched from Titan to vendors.
      </p>

      {items.length === 0 ? (
        <p className="text-sm text-gray-500">No dispatched materials found yet.</p>
      ) : (
        <div className="overflow-x-auto rounded border">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-600">SAP Doc No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">DC No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Material</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Model</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Front Qty</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Back Qty</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Dispatch Date</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((item) => (
                <tr key={item.sap_document_no}>
                  <td className="px-4 py-2 font-mono text-xs">{item.sap_document_no}</td>
                  <td className="px-4 py-2">{item.dc_no ?? "—"}</td>
                  <td className="px-4 py-2">{item.vendor_name}</td>
                  <td className="px-4 py-2">{item.material_code}</td>
                  <td className="px-4 py-2">{item.model ?? "—"}</td>
                  <td className="px-4 py-2 text-right">{item.quantity_front_case ?? "—"}</td>
                  <td className="px-4 py-2 text-right">{item.quantity_back_case ?? "—"}</td>
                  <td className="px-4 py-2">{item.dispatch_date ?? "—"}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        STATUS_STYLES[item.verification_status ?? "pending"] ?? STATUS_STYLES.pending
                      }`}
                    >
                      {item.verification_status ?? "pending"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}