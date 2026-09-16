// M7 Deviation Management
// Server component — read-only list, same pattern as M3 SAP Material
// Outward. No actions on this screen yet (resolving a deviation, e.g.
// once the vendor sends a corrected DC, is a later piece — see the
// vendor_status field, currently always "awaiting_response").

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
  created_at: string;
}

const MAIL_STATUS_STYLES: Record<string, string> = {
  sent: "bg-green-100 text-green-800",
  pending: "bg-gray-100 text-gray-700",
  no_email_on_file: "bg-amber-100 text-amber-800",
};

async function getDeviations(): Promise<DeviationItem[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const res = await fetch(`${baseUrl}/deviations/list`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to load deviations (status ${res.status})`);
  }

  return res.json();
}

export default async function DeviationManagementPage() {
  const deviations = await getDeviations();

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M7 — Deviation Management</h1>
      <p className="mb-4 text-sm text-gray-500">
        Delivery challans where the received quantity was less than expected.
      </p>

      {deviations.length === 0 ? (
        <p className="text-sm text-gray-500">No deviations recorded yet.</p>
      ) : (
        <div className="overflow-x-auto rounded border">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-600">DC No</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Material</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Expected</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Actual</th>
                <th className="px-4 py-2 text-right font-medium text-gray-600">Difference</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor Notified</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Vendor Status</th>
                <th className="px-4 py-2 text-left font-medium text-gray-600">Raised</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {deviations.map((d) => (
                <tr key={d.dc_no}>
                  <td className="px-4 py-2">{d.dc_no}</td>
                  <td className="px-4 py-2">{d.vendor_name}</td>
                  <td className="px-4 py-2">{d.material_code}</td>
                  <td className="px-4 py-2 text-right">{d.expected_qty}</td>
                  <td className="px-4 py-2 text-right">{d.actual_qty}</td>
                  <td className="px-4 py-2 text-right font-medium text-red-700">
                    -{d.difference_qty}
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        MAIL_STATUS_STYLES[d.mail_status] ?? MAIL_STATUS_STYLES.pending
                      }`}
                    >
                      {d.mail_status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-xs text-gray-500">{d.vendor_status}</td>
                  <td className="px-4 py-2 text-xs text-gray-500">
                    {new Date(d.created_at).toLocaleString()}
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