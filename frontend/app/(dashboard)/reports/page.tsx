// M14 Reports — Material Movement History
// Server component, read-only. Merges three sources we already store
// (DC verification, QC acknowledgement, SAP movement postings) into one
// timeline per delivery challan. Deliberately does not show storage
// location or a per-event quantity-moved figure — those remain unconfirmed
// per the SAP mapping design doc (Section 3).

interface MovementHistoryEvent {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  event_type: string;
  description: string;
  quantity: number | null;
  event_date: string;
}

const EVENT_STYLES: Record<string, string> = {
  received: "bg-blue-100 text-blue-800",
  qc_acknowledged: "bg-green-100 text-green-800",
  sap_movement: "bg-purple-100 text-purple-800",
};

const EVENT_LABELS: Record<string, string> = {
  received: "Received",
  qc_acknowledged: "QC Acknowledged",
  sap_movement: "SAP Movement",
};

async function getMovementHistory(): Promise<MovementHistoryEvent[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const res = await fetch(`${baseUrl}/reports/material-movement-history`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load movement history (status ${res.status})`);
  }
  return res.json();
}

export default async function ReportsPage() {
  const events = await getMovementHistory();

  const grouped = events.reduce<Record<string, MovementHistoryEvent[]>>((acc, e) => {
    (acc[e.dc_no] ??= []).push(e);
    return acc;
  }, {});

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold">M14 — Reports</h1>
      <p className="mb-4 text-sm text-gray-500">
        Material movement history — receipt, QC acknowledgement, and SAP movement
        postings, combined per delivery challan.
      </p>

      {Object.keys(grouped).length === 0 ? (
        <p className="text-sm text-gray-500">No movement history recorded yet.</p>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([dcNo, dcEvents]) => (
            <div key={dcNo} className="max-w-3xl rounded border p-4">
              <div className="mb-3 flex items-baseline gap-2">
                <h2 className="font-semibold">{dcNo}</h2>
                <span className="text-xs text-gray-500">
                  {dcEvents[0].vendor_name} · {dcEvents[0].material_code}
                </span>
              </div>
              <ol className="space-y-2 border-l-2 border-gray-200 pl-4">
                {dcEvents.map((e, i) => (
                  <li key={i} className="text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium ${
                          EVENT_STYLES[e.event_type] ?? "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {EVENT_LABELS[e.event_type] ?? e.event_type}
                      </span>
                      <span className="text-xs text-gray-400">{e.event_date}</span>
                    </div>
                    <p className="mt-0.5 text-gray-700">
                      {e.description}
                      {e.quantity !== null && (
                        <span className="text-gray-500"> — qty {e.quantity}</span>
                      )}
                    </p>
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}



