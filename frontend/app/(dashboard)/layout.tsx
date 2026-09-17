// Shared layout for office/admin screens (M2–M16).
// Redesigned app shell: sidebar with active-route highlighting and
// icons, collapsing into a mobile drawer below the lg breakpoint, plus
// a top header with a hamburger toggle on mobile.

import { AppShell } from "@/components/layout/AppShell";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}