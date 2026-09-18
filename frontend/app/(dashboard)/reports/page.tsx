// M14 Reports — Material Movement History, redesigned. Merges DC
// verification, QC acknowledgement, and SAP movement postings into one
// timeline per delivery challan — logic unchanged from before.

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState } from "@/components/ui/States";

interface MovementHistoryEvent {
  dc_no: string;
  vendor_name: string;
  material_code: string;
  event_type: string;
  description: string;
  quantity: number | null;
  event_date: string;
}

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

/**
 * event_date arrives in two different shapes depending on source: SAP
 * movement postings are date-only ("2026-09-06"), while our own
 * received/qc_acknowledged events are full timestamps with microsecond
 * precision. Format both down to one consistent, clean date — the extra
 * time-of-day precision on our own events isn't meaningful next to SAP's
 * coarser date-only data, so showing it just added visual noise.
 * timeZone: "UTC" avoids a date-only string like "2026-09-06" shifting
 * to the previous day when the browser is in a negative UTC offset.
 */
function formatEventDate(raw: string): string {
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

async function getMovementHistory(): Promise<MovementHistoryEvent[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const res = await fetch(`${baseUrl}/reports/material-movement-history`, { cache: "no-store" });
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
    <div>
      <PageHeader
        title="Reports"
        description="Material movement history — receipt, QC acknowledgement, and SAP movement postings, combined per delivery challan."
      />

      {Object.keys(grouped).length === 0 ? (
        <EmptyState
          title="No movement history yet"
          description="History will appear here once delivery challans are received and processed."
        />
      ) : (
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
                        {e.quantity !== null && (
                          <span className="text-text-secondary"> — qty {e.quantity}</span>
                        )}
                      </p>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}