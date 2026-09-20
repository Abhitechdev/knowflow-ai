"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, MessageSquare, Files, Search, ShieldAlert, Cpu } from "lucide-react";

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/", icon: Cpu, active: pathname === "/" },
    { name: "Ask AI", href: "/chat", icon: MessageSquare, active: pathname.startsWith("/chat") },
    { name: "Documents", href: "/documents", icon: Files, active: pathname.startsWith("/documents") },
    { name: "Search", href: "/search", icon: Search, active: pathname.startsWith("/search") },
    { name: "Admin / Eval", href: "/admin", icon: ShieldAlert, active: pathname.startsWith("/admin") },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-surface-muted/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface text-text-primary shadow-inner">
            <BookOpen className="h-5 w-5 text-accent" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold tracking-tight text-text-primary">KnowFlow AI</span>
              <span className="rounded-full border border-success/20 bg-success/10 px-2 py-0.5 text-[10px] font-medium text-success">
                Gate 5E Verified
              </span>
            </div>
            <p className="text-[11px] text-text-muted hidden sm:block">Enterprise Knowledge & SOP Agent</p>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group relative flex items-center space-x-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${
                  item.active
                    ? "bg-surface text-text-primary shadow-sm border border-border"
                    : "text-text-muted hover:bg-surface hover:text-text-primary"
                }`}
              >
                <Icon className="h-3.5 w-3.5 shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* User / Workspace indicator */}
        <div className="flex items-center space-x-2">
          <div className="hidden sm:flex items-center space-x-2 rounded-md border border-border bg-surface px-2.5 py-1 text-xs text-text-muted">
            <span className="h-2 w-2 rounded-full bg-text-muted"></span>
            <span>Personal Workspace</span>
          </div>
        </div>
      </div>
    </header>
  );
}
