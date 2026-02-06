import React from "react";

type ScrollAreaProps = React.HTMLAttributes<HTMLDivElement>;

export function ScrollArea({ className, ...props }: ScrollAreaProps) {
  return (
    <div
      className={`overflow-auto rounded-lg ${className ?? ""}`}
      {...props}
    />
  );
}
