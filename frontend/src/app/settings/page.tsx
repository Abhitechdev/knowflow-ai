"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth, HealthData } from "@/lib/api";
import { User, Server, Database, Shield, Cpu, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemHealth().then((res) => {
      setHealth(res.data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-text-primary">Settings & Profile</h1>
        <p className="text-xs text-text-muted mt-1">
          Workspace administration, system environment, and backend service status.
        </p>
      </div>

      {/* User Profile Card */}
      <div className="rounded-xl border border-border bg-surface-muted p-5 space-y-4">
        <h2 className="text-sm font-semibold text-text-primary">Current Session</h2>
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface text-text-primary">
            <User className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-text-primary">Workspace Administrator</p>
            <p className="text-[11px] text-text-muted">Role: ADMIN</p>
          </div>
        </div>
      </div>

      {/* Workspace Settings */}
      <div className="rounded-xl border border-border bg-surface-muted p-5 space-y-4">
        <h2 className="text-sm font-semibold text-text-primary">Active Workspace</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-border bg-surface p-3 space-y-1">
            <span className="text-text-muted text-[11px]">Workspace Name</span>
            <p className="font-medium text-text-primary">Personal Workspace</p>
          </div>
          <div className="rounded-lg border border-border bg-surface p-3 space-y-1">
            <span className="text-text-muted text-[11px]">Tenant Isolation</span>
            <p className="font-medium text-success">Enabled (Schema Enforced)</p>
          </div>
        </div>
      </div>

      {/* Backend & Environment Status */}
      <div className="rounded-xl border border-border bg-surface-muted p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-primary">Backend Infrastructure Status</h2>
          {loading && <RefreshCw className="h-3.5 w-3.5 text-text-muted animate-spin" />}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-border bg-surface p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-text-muted">
              <Server className="h-4 w-4" />
              <span className="font-medium">FastAPI Endpoint</span>
            </div>
            <div className="text-[11px] font-mono text-text-primary">
              {process.env.NEXT_PUBLIC_API_URL || (process.env.NEXT_PUBLIC_ENV === "development" ? "http://localhost:8000" : "Unconfigured")}
            </div>
            <p className="text-[11px] text-text-muted">
              Status: <span className="text-success font-semibold">{health ? health.status : "Probing..."}</span>
            </p>
          </div>

          <div className="rounded-lg border border-border bg-surface p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-text-muted">
              <Database className="h-4 w-4" />
              <span className="font-medium">Database (PostgreSQL)</span>
            </div>
            <div className="text-[11px] font-mono text-text-primary">
              Status: {health ? health.database.status : "Probing..."}
            </div>
            <p className="text-[11px] text-text-muted">
              Target: Supabase PostgreSQL with pgvector extension
            </p>
          </div>

          <div className="rounded-lg border border-border bg-surface p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-text-muted">
              <Shield className="h-4 w-4" />
              <span className="font-medium">Identity Provider</span>
            </div>
            <div className="text-[11px] font-mono text-text-primary">
              Provider: {health ? health.auth.provider : "supabase"}
            </div>
            <p className="text-[11px] text-text-muted">
              State: {health?.auth.configured ? "Configured" : "Unconfigured (Local fallback)"}
            </p>
          </div>

          <div className="rounded-lg border border-border bg-surface p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-text-muted">
              <Cpu className="h-4 w-4" />
              <span className="font-medium">AI Abstraction Architecture</span>
            </div>
            <div className="text-[11px] font-mono text-text-primary">
              Configured for Phase 3
            </div>
            <p className="text-[11px] text-text-muted">
              Replaceable LLM & Embedding provider adapters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
