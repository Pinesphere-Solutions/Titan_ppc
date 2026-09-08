"use client";

// Shared hook for capturing input from the HID/keyboard-wedge barcode
// scanners (Wireless Barcode Scanner + Barcode Scanner with Display).
// Both devices "type" the scanned code into whatever field is focused,
// terminated by Enter. This hook listens for a fast burst of keystrokes
// ending in Enter and treats that as a scan, distinguishing it from slow
// manual typing. See architecture doc Section 5.1 / 7.4.
//
// Server-side validation of the scanned code's format/checksum still
// happens on the backend (Section 7.4) — this hook only captures input.

import { useEffect, useRef } from "react";

const SCAN_GAP_THRESHOLD_MS = 30; // keystrokes faster than this = scanner, not typing
const MIN_SCAN_LENGTH = 4;

export function useScannerInput(onScan: (code: string) => void) {
  const buffer = useRef("");
  const lastKeyTime = useRef(0);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const now = Date.now();
      const gap = now - lastKeyTime.current;
      lastKeyTime.current = now;

      if (gap > SCAN_GAP_THRESHOLD_MS * 10) {
        // Long pause before this keystroke — start of a new potential scan.
        buffer.current = "";
      }

      if (e.key === "Enter") {
        if (buffer.current.length >= MIN_SCAN_LENGTH) {
          onScan(buffer.current);
        }
        buffer.current = "";
        return;
      }

      if (e.key.length === 1) {
        buffer.current += e.key;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onScan]);
}
