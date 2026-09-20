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
    <header className="sticky top-0 z-50 border-b border-zinc-800/80 bg-zinc-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-700/80 bg-zinc-900 text-zinc-100 shadow-inner">
            <BookOpen className="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold tracking-tight text-zinc-100">KnowFlow AI</span>
              <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
                Phase 1 Verified
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block">Enterprise Knowledge & SOP Agent</p>
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
                    ? "bg-zinc-800/90 text-zinc-100 shadow-sm border border-zinc-700/60"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
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
          <div className="hidden sm:flex items-center space-x-2 rounded-md border border-zinc-800 bg-zinc-900/80 px-2.5 py-1 text-xs text-zinc-300">
            <span className="h-2 w-2 rounded-full bg-zinc-500"></span>
            <span>Default Workspace</span>
          </div>
        </div>
      </div>
    </header>
  );
}
