"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface RadioGroupContextValue {
  value: string;
  onChange: (value: string) => void;
  name: string;
}

const RadioGroupContext = React.createContext<RadioGroupContextValue | null>(null);

interface RadioGroupProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  value: string;
  onValueChange: (value: string) => void;
  name?: string;
}

function RadioGroup({ value, onValueChange, name = "radio", className, ...props }: RadioGroupProps) {
  return (
    <RadioGroupContext.Provider value={{ value, onChange: onValueChange, name }}>
      <div role="radiogroup" className={cn("grid gap-2", className)} {...props} />
    </RadioGroupContext.Provider>
  );
}

interface RadioGroupItemProps extends React.HTMLAttributes<HTMLButtonElement> {
  value: string;
}

function RadioGroupItem({ value: itemValue, className, children, ...props }: RadioGroupItemProps) {
  const ctx = React.useContext(RadioGroupContext);
  if (!ctx) throw new Error("RadioGroupItem must be used within <RadioGroup>");

  const isSelected = ctx.value === itemValue;

  return (
    <button
      type="button"
      role="radio"
      aria-checked={isSelected}
      onClick={() => ctx.onChange(itemValue)}
      className={cn(
        "aspect-square h-4 w-4 rounded-full border border-[var(--primary)] text-[var(--primary)] ring-offset-[var(--background)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    >
      {isSelected && (
        <span className="flex items-center justify-center">
          <span className="h-2.5 w-2.5 rounded-full bg-current" />
        </span>
      )}
    </button>
  );
}

export { RadioGroup, RadioGroupItem };
