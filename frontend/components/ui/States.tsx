import { AlertCircle, Inbox, Loader2 } from "lucide-react";
import { ReactNode } from "react";

export function EmptyState({
  title = "Nothing here yet",
  description,
  icon,
}: {
  title?: string;
  description?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface px-6 py-12 text-center">
      <div className="mb-3 text-text-muted">{icon ?? <Inbox className="h-8 w-8" />}</div>
      <p className="text-sm font-medium text-text-primary">{title}</p>
      {description && <p className="mt-1 text-sm text-text-secondary">{description}</p>}
    </div>
  );
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-8 text-sm text-text-secondary">
      <Loader2 className="h-4 w-4 animate-spin" />
      {label}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-error-bg bg-error-bg px-4 py-3 text-sm text-error-text">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{message}</span>
    </div>
  );
}