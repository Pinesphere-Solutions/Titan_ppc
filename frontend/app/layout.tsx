import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: "PPC CBE Tracking Application",
  description: "Sub-contractor material tracking — Titan PPC CBE",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      {/* suppressHydrationWarning: browser extensions like Grammarly inject
          attributes (data-gr-ext-installed, data-new-gr-c-s-check-loaded)
          onto <body> after the server sends it but before React hydrates.
          That's a real, harmless mismatch caused by the extension, not our
          code — this silences just that false-positive warning on <body>. */}
      <body className="min-h-full flex flex-col font-sans" suppressHydrationWarning>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
