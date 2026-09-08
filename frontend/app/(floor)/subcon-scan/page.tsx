// Floor station: Sub-con Receiving Scan
// Scan-first kiosk screen for the Sub-con team — see architecture doc Section 5.1

export default function SubconScanPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-6">
      <h1 className="mb-2 text-2xl font-semibold">Sub-con Receiving</h1>
      <p className="text-gray-500">Scan the White Box QR to log receiving and set category.</p>
      {/* TODO: wire up useScannerInput() and POST to /receiving/subcon */}
    </div>
  );
}
