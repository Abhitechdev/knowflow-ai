"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Search,
  History,
  Settings,
  Menu,
  X,
  BookOpen,
  User,
  ShieldCheck,
} from "lucide-react";
import { BackendStatusIndicator } from "./backend-status-indicator";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Ask AI", href: "/chat", icon: MessageSquare },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Search", href: "/search", icon: Search },
  { name: "History", href: "/history", icon: History, badge: "Phase 4" },
  { name: "Settings & Profile", href: "/settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between border-b border-zinc-800/80 bg-zinc-950/90 px-4 py-3 sticky top-0 z-50 backdrop-blur-md">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-900 text-indigo-400">
            <BookOpen className="h-4 w-4" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-white">KnowFlow AI</span>
        </div>

        <div className="flex items-center space-x-3">
          <BackendStatusIndicator compact />
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="rounded-md p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white"
            aria-label="Toggle Menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 flex-col justify-between border-r border-zinc-800/80 bg-zinc-950/60 p-4 shrink-0 sticky top-0 h-screen">
        <div className="space-y-6">
          {/* Logo / Brand */}
          <div className="flex items-center space-x-3 px-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-zinc-700/80 bg-zinc-900 text-indigo-400 shadow-inner">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-sm tracking-tight text-white">KnowFlow AI</span>
                <span className="rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-medium text-emerald-400 border border-emerald-500/20">
                  P1
                </span>
              </div>
              <p className="text-[11px] text-zinc-400">Enterprise SOP Agent</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                    active
                      ? "bg-zinc-800/90 text-white border border-zinc-700/60 shadow-sm"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="rounded border border-zinc-800 bg-zinc-900/80 px-1.5 py-0.5 text-[9px] font-normal text-zinc-500">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Sidebar: Real Backend Status & User Profile */}
        <div className="space-y-3 pt-4 border-t border-zinc-800/80">
          <BackendStatusIndicator />

          <div className="flex items-center justify-between rounded-lg border border-zinc-800/60 bg-zinc-900/40 p-2.5">
            <div className="flex items-center space-x-2.5 min-w-0">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-zinc-800 text-zinc-300">
                <User className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-zinc-200 truncate">Default Workspace</p>
                <p className="text-[10px] text-zinc-500 truncate">Workspace Admin</p>
              </div>
            </div>
            <ShieldCheck className="h-4 w-4 text-zinc-500 shrink-0" />
          </div>
        </div>
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={() => setMobileOpen(false)}>
          <div
            className="w-4/5 max-w-xs h-full bg-zinc-950 border-r border-zinc-800 p-4 flex flex-col justify-between"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="space-y-4">
              <div className="flex items-center space-x-2.5 px-2 pb-3 border-b border-zinc-800">
                <BookOpen className="h-5 w-5 text-indigo-400" />
                <span className="font-semibold text-sm text-white">KnowFlow AI</span>
              </div>

              <nav className="space-y-1">
                {NAV_ITEMS.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium ${
                        active
                          ? "bg-zinc-800 text-white"
                          : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                      }`}
                    >
                      <div className="flex items-center space-x-2.5">
                        <Icon className="h-4 w-4 shrink-0" />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span className="rounded bg-zinc-900 px-1.5 py-0.5 text-[9px] text-zinc-500">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>

            <div className="space-y-3 pt-4 border-t border-zinc-800">
              <BackendStatusIndicator />
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Bar */}
        <header className="hidden md:flex h-14 items-center justify-between border-b border-zinc-800/80 bg-zinc-950/40 px-6 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-medium text-zinc-400">Environment:</span>
            <span className="rounded-md border border-zinc-800 bg-zinc-900/80 px-2 py-0.5 font-mono text-[11px] text-zinc-300">
              development
            </span>
            <span className="text-zinc-600">•</span>
            <span className="text-xs text-zinc-400">Phase 1: Foundation Architecture</span>
          </div>

          <div className="flex items-center space-x-4">
            <BackendStatusIndicator compact />
            <div className="h-4 w-px bg-zinc-800" />
            <span className="text-xs text-zinc-400">v0.1.0</span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
