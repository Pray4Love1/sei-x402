import React from "react";

type ButtonVariant = "default" | "outline" | "ghost";

type ButtonSize = "default" | "sm";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

const variantClasses: Record<ButtonVariant, string> = {
  default: "bg-slate-900 text-white hover:bg-slate-800",
  outline:
    "border border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-slate-900",
  ghost: "text-slate-600 hover:bg-slate-100",
};

const sizeClasses: Record<ButtonSize, string> = {
  default: "px-4 py-2 text-sm",
  sm: "px-3 py-1.5 text-xs",
};

export function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-md font-medium transition ${
        variantClasses[variant]
      } ${sizeClasses[size]} ${className ?? ""}`}
      {...props}
    />
  );
}
