// Shared layout for office/admin screens (M2–M16).
// TODO: replace with real role-aware navigation once auth (M1) is wired up.

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/sap-outward", label: "SAP Material Outward" },
  { href: "/receiving", label: "Material Receiving" },
  { href: "/dc-verification", label: "DC Verification" },
  { href: "/physical-verification", label: "Physical Verification" },
  { href: "/deviations", label: "Deviation Management" },
  { href: "/qc-acknowledgement", label: "QC Acknowledgement" },
  { href: "/sap-processing", label: "SAP Processing" },
  { href: "/ppc-collection", label: "PPC Collection" },
  { href: "/qa-inspection", label: "QA Inspection" },
  { href: "/zqmtl1", label: "ZQMTL1 Processing" },
  { href: "/storage", label: "Storage Management" },
  { href: "/reports", label: "Reports" },
  { href: "/masters", label: "Masters" },
  { href: "/settings", label: "Settings" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r p-4">
        <div className="mb-4 text-sm font-semibold">PPC CBE Tracking Application</div>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="block rounded px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-100"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
