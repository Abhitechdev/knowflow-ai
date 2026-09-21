"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { User, ShieldCheck, ArrowRight, Lock, Building, Info } from "lucide-react";

export default function SettingsPage() {
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email ?? null);
      }
    });
  }, [supabase.auth]);

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-text-primary">Settings & Profile</h1>
        <p className="text-xs text-text-muted mt-1">
          Manage your account profile, workspace details, and security policies.
        </p>
      </div>

      {/* User Profile Card */}
      <div className="rounded-xl border border-border bg-surface p-5 space-y-4">
        <h2 className="text-sm font-semibold text-text-primary">User Account</h2>
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface-muted text-text-primary shrink-0">
            <User className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-text-primary truncate">{userEmail || "Workspace User"}</p>
            <p className="text-[11px] text-text-muted">Account Status: Active</p>
          </div>
        </div>
      </div>

      {/* Workspace Settings */}
      <div className="rounded-xl border border-border bg-surface p-5 space-y-4">
        <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
          <Building className="h-4 w-4 text-accent" />
          Workspace Configuration
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-border bg-surface-muted p-3 space-y-1">
            <span className="text-text-muted text-[11px]">Workspace Clearance</span>
            <p className="font-medium text-text-primary">Enterprise Dedicated Partition</p>
          </div>
          <div className="rounded-lg border border-border bg-surface-muted p-3 space-y-1">
            <span className="text-text-muted text-[11px]">Tenant Isolation</span>
            <p className="font-medium text-success">Active (PostgreSQL Row-Level Security)</p>
          </div>
        </div>
      </div>

      {/* Security & Data Compliance */}
      <div className="rounded-xl border border-border bg-surface p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-success" />
            Security & DPDP Act Compliance
          </h2>
          <Link
            href="/security"
            className="text-xs font-medium text-accent hover:underline inline-flex items-center gap-1"
          >
            Review Trust Center <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
        <p className="text-xs text-text-muted leading-relaxed">
          KnowFlow AI is aligned with India&apos;s Digital Personal Data Protection Act, 2023 (DPDPA) and GDPR. All documents are encrypted with AES-256 at rest and TLS 1.3 in transit.
        </p>
      </div>

      {/* About Application */}
      <div className="rounded-xl border border-border bg-surface p-5 space-y-3 text-xs">
        <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
          <Info className="h-4 w-4 text-text-muted" />
          About KnowFlow AI
        </h2>
        <p className="text-text-muted leading-relaxed">
          Enterprise SOP and Knowledge Assistant with verified citations and guaranteed grounded answering policy.
        </p>
        <div className="text-text-muted pt-2 text-[11px]">
          Version: 0.1.0 • Multi-tenant Knowledge Engine
        </div>
      </div>
    </div>
  );
}
