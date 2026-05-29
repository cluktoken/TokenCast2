"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  LayoutDashboard, MonitorSmartphone, LayoutGrid, Sparkles, LogOut,
} from "lucide-react";
import { useAuth } from "@/store/auth";
import { Spinner } from "./ui";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/displays", label: "Displays", icon: MonitorSmartphone },
  { href: "/layouts", label: "Layouts", icon: LayoutGrid },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, initialized, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (initialized && !user) router.replace("/login");
  }, [initialized, user, router]);

  if (!initialized) return <Spinner />;
  if (!user) return null;

  return (
    <div className="flex min-h-screen">
      <aside
        className="tc-surface flex w-60 flex-col border-r p-4"
        style={{ borderColor: "var(--tc-border)" }}
      >
        <Link href="/dashboard" className="mb-6 flex items-center gap-2 px-2 text-lg font-bold">
          <Sparkles className="tc-accent-text h-5 w-5" /> TokenCast
        </Link>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition",
                pathname.startsWith(href) ? "tc-accent text-white" : "hover:opacity-70",
              )}
            >
              <Icon className="h-4 w-4" /> {label}
            </Link>
          ))}
        </nav>
        <div className="mt-4 border-t pt-4 text-sm" style={{ borderColor: "var(--tc-border)" }}>
          <div className="px-3 tc-muted truncate">{user.email}</div>
          <button
            onClick={() => { void logout().then(() => router.replace("/login")); }}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:opacity-70"
          >
            <LogOut className="h-4 w-4" /> Log out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  );
}
