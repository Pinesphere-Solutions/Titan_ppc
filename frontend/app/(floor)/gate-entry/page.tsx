// Floor station: Gate Entry
// Scan-first kiosk screen for Gate Security — see architecture doc Section 5.1
// Uses the shared useScannerInput() hook to capture White Box QR scans from
// the HID barcode scanners (wireless + display models).

export default function GateEntryPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-6">
      <h1 className="mb-2 text-2xl font-semibold">Gate Entry</h1>
      <p className="text-gray-500">Scan the White Box QR to log inward entry.</p>
      {/* TODO: wire up useScannerInput() and POST to /receiving/gate-entry */}
    </div>
  );
}
