import React from "react";

const variantStyles: Record<string, string> = {
  default: "bg-slate-900 text-white",
  outline: "border border-slate-200 text-slate-700",
  secondary: "bg-slate-100 text-slate-700",
};

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "outline" | "secondary";
};

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const styles = variantStyles[variant] ?? variantStyles.default;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${styles} ${
        className ?? ""
      }`}
      {...props}
    />
  );
}
