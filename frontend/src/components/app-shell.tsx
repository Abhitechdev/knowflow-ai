"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
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
  LogOut,
} from "lucide-react";
import { BackendStatusIndicator } from "./backend-status-indicator";
import { createClient } from "@/lib/supabase/client";

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
  { name: "History", href: "/history", icon: History },
  { name: "Settings & Profile", href: "/settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();
  
  const envName = process.env.NEXT_PUBLIC_ENV || "development";

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email ?? null);
      }
    });

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setUserEmail(session?.user?.email ?? null);
      if (event === 'SIGNED_OUT') {
        router.push("/login");
      }
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, [supabase.auth, router]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  const isPublicRoute =
    pathname.startsWith("/security") ||
    pathname.startsWith("/login") ||
    pathname.startsWith("/register") ||
    pathname.startsWith("/reset-password") ||
    pathname.startsWith("/update-password") ||
    (pathname === "/" && !userEmail);

  if (isPublicRoute) {
    return <div className="min-h-screen bg-background text-text-primary">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-background text-text-primary flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between border-b border-border bg-surface px-4 py-3 sticky top-0 z-50 backdrop-blur-md">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-surface-muted text-accent">
            <BookOpen className="h-4 w-4" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-text-primary">KnowFlow AI</span>
        </div>

        <div className="flex items-center space-x-3">
          <BackendStatusIndicator compact />
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="rounded-md p-1.5 text-text-muted hover:bg-surface-hover hover:text-text-primary"
            aria-label="Toggle Menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 flex-col justify-between border-r border-border bg-surface p-4 shrink-0 sticky top-0 h-screen">
        <div className="space-y-6">
          {/* Logo / Brand */}
          <div className="flex items-center space-x-3 px-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface-muted text-accent shadow-sm">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-sm tracking-tight text-text-primary">KnowFlow AI</span>
              </div>
              <p className="text-[11px] text-text-muted">Enterprise SOP Agent</p>
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
                      ? "bg-surface-active text-text-primary border border-border shadow-sm"
                      : "text-text-muted hover:bg-surface-hover hover:text-text-primary"
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="rounded border border-border bg-surface-muted px-1.5 py-0.5 text-[9px] font-normal text-text-muted">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Sidebar: Real Backend Status & User Profile */}
        <div className="space-y-3 pt-4 border-t border-border">
          <BackendStatusIndicator />

          <div className="flex items-center justify-between rounded-lg border border-border bg-surface-muted p-2.5">
            <div className="flex items-center space-x-2.5 min-w-0">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-surface text-text-muted">
                <User className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-text-primary truncate">{userEmail || "User"}</p>
                <button onClick={handleSignOut} className="text-[10px] text-text-muted hover:text-text-primary truncate cursor-pointer transition-colors text-left flex items-center space-x-1">
                  <span>Sign out</span>
                  <LogOut className="h-2.5 w-2.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={() => setMobileOpen(false)}>
          <div
            className="w-4/5 max-w-xs h-full bg-background border-r border-border p-4 flex flex-col justify-between"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="space-y-4">
              <div className="flex items-center space-x-2.5 px-2 pb-3 border-b border-border">
                <BookOpen className="h-5 w-5 text-accent" />
                <span className="font-semibold text-sm text-text-primary">KnowFlow AI</span>
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
                          ? "bg-surface-active text-text-primary border border-border"
                          : "text-text-muted hover:bg-surface-hover hover:text-text-primary"
                      }`}
                    >
                      <div className="flex items-center space-x-2.5">
                        <Icon className="h-4 w-4 shrink-0" />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span className="rounded border border-border bg-surface-muted px-1.5 py-0.5 text-[9px] text-text-muted">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>

            <div className="space-y-3 pt-4 border-t border-border">
              <BackendStatusIndicator />
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Bar */}
        <header className="hidden md:flex h-14 items-center justify-between border-b border-border bg-surface px-6 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-medium text-text-muted">Environment:</span>
            <span className="rounded-md border border-border bg-surface-muted px-2 py-0.5 font-mono text-[11px] text-text-primary capitalize">
              {envName}
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <BackendStatusIndicator compact />
            <div className="h-4 w-px bg-border" />
            <span className="text-xs text-text-muted">v0.1.0</span>
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
