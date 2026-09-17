import { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes } from "react";

export function Table({ className = "", ...props }: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <table className={`min-w-full divide-y divide-border text-sm ${className}`} {...props} />
    </div>
  );
}

export function TableHead({ className = "", ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <thead className={`bg-neutral-bg ${className}`} {...props} />;
}

export function TableBody({ className = "", ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className={`divide-y divide-border ${className}`} {...props} />;
}

export function TableRow({ className = "", ...props }: HTMLAttributes<HTMLTableRowElement>) {
  return <tr className={`transition-colors hover:bg-neutral-bg/60 ${className}`} {...props} />;
}

export function TableHeaderCell({
  align = "left",
  className = "",
  ...props
}: ThHTMLAttributes<HTMLTableCellElement> & { align?: "left" | "right" | "center" }) {
  const alignClass = align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left";
  return (
    <th
      className={`px-4 py-2.5 font-medium text-text-secondary ${alignClass} ${className}`}
      {...props}
    />
  );
}

export function TableCell({
  align = "left",
  className = "",
  ...props
}: TdHTMLAttributes<HTMLTableCellElement> & { align?: "left" | "right" | "center" }) {
  const alignClass = align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left";
  return <td className={`px-4 py-2.5 text-text-primary ${alignClass} ${className}`} {...props} />;
}