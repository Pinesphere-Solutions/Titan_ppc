// M9 SAP Processing
// Server component — read-only list of movement records (101/313/321),
// same pattern as M3 SAP Material Outward and M7 Deviation Management.

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

const MOVEMENT_TYPE_STYLES: Record<string, string> = {
  "101": "bg-blue-100 text-blue-800",
  "313": "bg-purple-100 text-purple-800",
  "321": "bg-teal-100 text-teal-800",
};

async function getMovements(): Promise<MovementItem[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M9 — SAP Processing</h1>
      <p className="mb-4 text-sm text-gray-500">
        Movement records synced from SAP: goods receipt, stock transfer, and quality to
        unrestricted stock.
      </p>

      {movements.length === 0 ? (
        <p className="text-sm text-gray-500">No movement records synced yet.</p>
      ) : (
        <div className="overflow-x-auto rounded border">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Material Document No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Movement Type</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">DC No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Posting Date</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Sync Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {movements.map((m) => (
                <tr key={m.material_document_no}>
                  <td className="px-4 py-2 font-mono text-xs">{m.material_document_no}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        MOVEMENT_TYPE_STYLES[m.movement_type] ?? "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {MOVEMENT_TYPE_LABELS[m.movement_type] ?? m.movement_type}
                    </span>
                  </td>
                  <td className="px-4 py-2">{m.dc_no}</td>
                  <td className="px-4 py-2">{m.posting_date ?? "—"}</td>
                  <td className="px-4 py-2 text-xs text-gray-500">{m.sync_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}



