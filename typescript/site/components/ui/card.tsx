import React from "react";

type CardProps = React.HTMLAttributes<HTMLDivElement>;

type CardTitleProps = React.HTMLAttributes<HTMLHeadingElement>;

type CardDescriptionProps = React.HTMLAttributes<HTMLParagraphElement>;

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white ${className ?? ""}`}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: CardProps) {
  return <div className={`p-6 ${className ?? ""}`} {...props} />;
}

export function CardTitle({ className, ...props }: CardTitleProps) {
  return (
    <h3 className={`text-lg font-semibold text-slate-900 ${className ?? ""}`} {...props} />
  );
}

export function CardDescription({ className, ...props }: CardDescriptionProps) {
  return (
    <p className={`text-sm text-slate-500 ${className ?? ""}`} {...props} />
  );
}

export function CardContent({ className, ...props }: CardProps) {
  return <div className={`px-6 pb-6 ${className ?? ""}`} {...props} />;
}
