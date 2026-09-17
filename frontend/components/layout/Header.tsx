"use client";

import { Menu } from "lucide-react";
import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "./Sidebar";

export function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const pathname = usePathname();
  const current = NAV_ITEMS.find((item) => item.href === pathname);

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-border bg-surface px-4 sm:px-6">
      <button
        onClick={onMenuClick}
        aria-label="Open menu"
        className="text-text-secondary lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>
      <h1 className="truncate text-sm font-semibold text-text-primary">
        {current?.label ?? "PPC CBE Tracking Application"}
      </h1>
    </header>
  );
}