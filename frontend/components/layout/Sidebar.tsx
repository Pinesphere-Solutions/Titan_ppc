"use client";

import {
  AlertTriangle,
  BadgeCheck,
  BarChart3,
  ClipboardCheck,
  Database,
  GitBranch,
  Inbox,
  LayoutDashboard,
  LogOut,
  PackageOpen,
  ScanLine,
  Search,
  Settings as SettingsIcon,
  Truck,
  Warehouse,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";

export const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/sap-outward", label: "SAP Material Outward", icon: Truck },
  { href: "/receiving", label: "Material Receiving", icon: Inbox },
  { href: "/dc-verification", label: "DC Verification", icon: ClipboardCheck },
  { href: "/physical-verification", label: "Physical Verification", icon: ScanLine },
  { href: "/deviations", label: "Deviation Management", icon: AlertTriangle },
  { href: "/qc-acknowledgement", label: "QC Acknowledgement", icon: BadgeCheck },
  { href: "/sap-processing", label: "SAP Processing", icon: GitBranch },
  { href: "/ppc-collection", label: "PPC Collection", icon: PackageOpen },
  { href: "/qa-inspection", label: "QA Inspection", icon: Search },
  { href: "/zqmtl1", label: "ZQMTL1 Processing", icon: Database },
  { href: "/storage", label: "Storage Management", icon: Warehouse },
  { href: "/reports", label: "Reports", icon: BarChart3 },
  { href: "/masters", label: "Masters", icon: Database },
  // adminOnly: M1 Role-based Access — Settings is the only module
  // gated by require_role("admin") on the backend today, so this is
  // the one nav item hidden by role. Everything else stays visible to
  // every logged-in role, since no other per-module access mapping
  // has been defined.
  { href: "/settings", label: "Settings", icon: SettingsIcon, adminOnly: true },
];

/**
 * Below the lg breakpoint this becomes a slide-in drawer with a backdrop,
 * controlled by isOpen/onClose (lifted into AppShell so the Header's
 * hamburger button can open it). At lg and above it's always visible as
 * a static column — the mobile-only classes simply have no effect there.
 */
export function Sidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<{ username: string; role: string }>("/auth/me")
      .then((res) => {
        setUsername(res.data.username);
        setRole(res.data.role);
      })
      .catch(() => {
        setUsername(null);
        setRole(null);
      });
  }, []);

  // Close the mobile drawer automatically whenever the route changes.
  useEffect(() => {
    onClose();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  async function handleLogout() {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      router.push("/login");
    }
  }

  const visibleNavItems = NAV_ITEMS.filter((item) => !item.adminOnly || role === "admin");

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex h-screen w-64 shrink-0 flex-col border-r border-border bg-surface transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-border px-5">
          <div className="flex items-center">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-sm font-bold text-white">
              P
            </div>
            <span className="ml-2.5 text-sm font-semibold text-text-primary">PPC CBE Tracking</span>
          </div>
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="text-text-secondary lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
          {visibleNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-light text-primary"
                    : "text-text-secondary hover:bg-neutral-bg hover:text-text-primary"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border p-3">
          <div className="flex items-center justify-between rounded-md px-2 py-2">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-text-primary">{username ?? "..."}</p>
            </div>
            <button
              onClick={handleLogout}
              aria-label="Log out"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-text-secondary transition-colors hover:bg-error-bg hover:text-error"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
