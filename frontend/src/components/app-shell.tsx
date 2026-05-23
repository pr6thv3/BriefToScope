"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell,
  Bolt,
  ChevronDown,
  FileText,
  LayoutDashboard,
  Search,
  Settings,
  Library,
  CreditCard,
  CheckCircle2,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Brand } from "@/components/brand";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/onboarding", label: "Onboarding", icon: CheckCircle2 },
  { href: "/generate", label: "Generate", icon: Bolt },
  { href: "/sow/demo-001", label: "Documents", icon: FileText },
  { href: "/templates", label: "Templates", icon: Library },
  { href: "/settings/billing", label: "Billing", icon: CreditCard },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const auth = useAppAuth();
  const workspaceName = auth.workspace?.name ?? "Workspace";
  const roleLabel = auth.role ? auth.role.replace("_", " ") : "member";
  const initials = workspaceName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase())
    .join("") || "BT";
  const visibleNavItems = navItems.filter((item) => {
    if (!auth.role) {
      return true;
    }
    if (item.href.startsWith("/settings/billing")) {
      return auth.can("billing:manage");
    }
    if (item.href.startsWith("/generate")) {
      return auth.can("sow:generate");
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-56 flex-col bg-slate-950 text-white lg:flex">
        <div className="flex h-16 items-center px-5">
          <Brand
            href="/dashboard"
            className="text-white"
            markClassName="bg-blue-500 shadow-blue-500/30"
          />
        </div>
        <nav className="flex flex-1 flex-col gap-2 px-3 py-4">
          {visibleNavItems.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-11 items-center gap-3 rounded-lg px-3 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white",
                  active && "bg-white/12 text-white"
                )}
              >
                <Icon className="size-5" aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3">
            <Avatar className="size-8">
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{workspaceName}</p>
              <p className="truncate text-xs capitalize text-slate-400">{roleLabel}</p>
            </div>
            <ChevronDown className="size-4 text-slate-400" aria-hidden="true" />
          </div>
        </div>
      </aside>

      <div className="lg:pl-56">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-white/90 px-4 backdrop-blur md:px-8">
          <div className="flex items-center gap-3 lg:hidden">
            <Brand href="/dashboard" />
          </div>
          <div className="hidden w-full max-w-sm items-center gap-2 rounded-lg border bg-white px-3 lg:flex">
            <Search className="size-4 text-slate-400" aria-hidden="true" />
            <Input
              className="h-10 border-0 px-0 shadow-none focus-visible:ring-0"
              placeholder="Search"
            />
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" aria-label="Notifications">
              <Bell data-icon="inline-start" />
            </Button>
            <Avatar className="size-8">
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <span className="hidden text-sm font-medium md:block">
              {workspaceName}
            </span>
            <ChevronDown className="size-4 text-slate-500" aria-hidden="true" />
          </div>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
