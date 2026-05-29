"use client";

import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes, InputHTMLAttributes } from "react";

export function Button({
  className,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "danger" }) {
  const variants = {
    primary: "tc-accent text-white hover:opacity-90",
    ghost: "tc-surface border hover:opacity-80",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "tc-surface w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2",
        className,
      )}
      style={{ borderColor: "var(--tc-border)" }}
      {...props}
    />
  );
}

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn("tc-surface rounded-xl border p-5", className)} style={{ borderColor: "var(--tc-border)" }}>
      {children}
    </div>
  );
}

export function Spinner() {
  return (
    <div className="flex h-32 items-center justify-center">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-current border-t-transparent opacity-60" />
    </div>
  );
}
