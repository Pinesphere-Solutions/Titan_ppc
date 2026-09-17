import { Loader2 } from "lucide-react";
import { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "outline" | "destructive" | "ghost";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  icon?: ReactNode;
}

const VARIANT_STYLES: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-primary-hover disabled:bg-primary/60",
  secondary:
    "bg-neutral-bg text-text-primary hover:bg-border disabled:opacity-60",
  outline:
    "border border-border text-text-primary hover:bg-neutral-bg disabled:opacity-60",
  destructive:
    "bg-error text-white hover:bg-error-text disabled:bg-error/60",
  ghost:
    "text-text-secondary hover:bg-neutral-bg disabled:opacity-60",
};

const SIZE_STYLES: Record<Size, string> = {
  sm: "px-2.5 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
};

/**
 * The one Button used everywhere in the app. Primary actions should be
 * the only "primary" variant visible on a given screen — see the UI
 * consistency guideline: avoid competing primary buttons.
 */
export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  disabled,
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors duration-150 disabled:cursor-not-allowed ${VARIANT_STYLES[variant]} ${SIZE_STYLES[size]} ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : icon}
      {children}
    </button>
  );
}