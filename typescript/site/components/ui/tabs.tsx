"use client";

import React from "react";

type TabsContextValue = {
  value: string;
  setValue: (value: string) => void;
};

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined);

type TabsProps = React.HTMLAttributes<HTMLDivElement> & {
  defaultValue: string;
};

export function Tabs({ defaultValue, className, ...props }: TabsProps) {
  const [value, setValue] = React.useState(defaultValue);
  return (
    <TabsContext.Provider value={{ value, setValue }}>
      <div className={className} {...props} />
    </TabsContext.Provider>
  );
}

type TabsListProps = React.HTMLAttributes<HTMLDivElement>;

export function TabsList({ className, ...props }: TabsListProps) {
  return (
    <div
      className={`inline-flex items-center rounded-lg border border-slate-200 bg-slate-50 p-1 ${
        className ?? ""
      }`}
      {...props}
    />
  );
}

type TabsTriggerProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  value: string;
};

export function TabsTrigger({
  value,
  className,
  ...props
}: TabsTriggerProps) {
  const context = React.useContext(TabsContext);
  if (!context) {
    throw new Error("TabsTrigger must be used within Tabs");
  }
  const isActive = context.value === value;
  return (
    <button
      className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
        isActive
          ? "bg-white text-slate-900 shadow"
          : "text-slate-500 hover:text-slate-900"
      } ${className ?? ""}`}
      onClick={() => context.setValue(value)}
      type="button"
      {...props}
    />
  );
}

type TabsContentProps = React.HTMLAttributes<HTMLDivElement> & {
  value: string;
};

export function TabsContent({ value, className, ...props }: TabsContentProps) {
  const context = React.useContext(TabsContext);
  if (!context) {
    throw new Error("TabsContent must be used within Tabs");
  }
  if (context.value !== value) {
    return null;
  }
  return <div className={className} {...props} />;
}
