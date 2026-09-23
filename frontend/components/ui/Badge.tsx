type BadgeVariant = "success" | "warning" | "error" | "info" | "neutral";

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  success: "bg-success-bg text-success-text",
  warning: "bg-warning-bg text-warning-text",
  error: "bg-error-bg text-error-text",
  info: "bg-info-bg text-info-text",
  neutral: "bg-neutral-bg text-neutral-text",
};

export function Badge({
  variant = "neutral",
  children,
}: {
  variant?: BadgeVariant;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${VARIANT_STYLES[variant]}`}
    >
      {children}
    </span>
  );
}

/**
 * Canonical status -> color mapping for the whole application. Every
 * screen that shows a status string (verification_status, qc_ack_status,
 * mail_status, vendor_status, ud_post_status, sync_status) should route
 * through this so the same underlying meaning always renders the same
 * color, no matter which screen it's on.
 */
const STATUS_VARIANT_MAP: Record<string, BadgeVariant> = {
  // success — the thing completed as expected
  verified: "success",
  done: "success",
  sent: "success",
  resolved: "success",
  posted: "success",
  synced: "success",
  completed: "success",
  // info — actively being worked, not just waiting
  in_progress: "info",
  // warning — waiting on something, not yet actioned
  pending: "warning",
  awaiting_response: "warning",
  no_email_on_file: "warning",
  not_posted: "warning",
  waiting_for_inspection: "warning",
  // error — a real problem occurred
  reverted: "error",
};

const STATUS_LABEL_OVERRIDES: Record<string, string> = {
  no_email_on_file: "No email on file",
  awaiting_response: "Awaiting response",
  not_posted: "Not posted",
  waiting_for_inspection: "Waiting for inspection",
  in_progress: "In progress",
};

export function StatusBadge({ status }: { status: string }) {
  const variant = STATUS_VARIANT_MAP[status] ?? "neutral";
  const label = STATUS_LABEL_OVERRIDES[status] ?? status;
  return <Badge variant={variant}>{label}</Badge>;
}