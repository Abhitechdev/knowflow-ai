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
        <h1 className="text-xl font-semibold tracking-tight text-white">Settings & Profile</h1>
        <p className="text-xs text-zinc-400 mt-1">
          Workspace administration, system environment, and backend service status.
        </p>
      </div>

      {/* User Profile Card */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-zinc-200">Current Session</h2>
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-zinc-200">
            <User className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-white">Default Workspace Administrator</p>
            <p className="text-[11px] text-zinc-400">Role: ADMIN • Local Development Mode</p>
          </div>
        </div>
      </div>

      {/* Workspace Settings */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-zinc-200">Active Workspace</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3 space-y-1">
            <span className="text-zinc-500 text-[11px]">Workspace Name</span>
            <p className="font-medium text-zinc-200">Default Workspace</p>
          </div>
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3 space-y-1">
            <span className="text-zinc-500 text-[11px]">Tenant Isolation</span>
            <p className="font-medium text-emerald-400">Enabled (Schema Enforced)</p>
          </div>
        </div>
      </div>

      {/* Backend & Environment Status */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-200">Backend Infrastructure Status</h2>
          {loading && <RefreshCw className="h-3.5 w-3.5 text-zinc-500 animate-spin" />}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-zinc-400">
              <Server className="h-4 w-4" />
              <span className="font-medium">FastAPI Endpoint</span>
            </div>
            <div className="text-[11px] font-mono text-zinc-300">
              {process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}
            </div>
            <p className="text-[11px] text-zinc-500">
              Status: <span className="text-emerald-400 font-semibold">{health ? health.status : "Probing..."}</span>
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-zinc-400">
              <Database className="h-4 w-4" />
              <span className="font-medium">Database (PostgreSQL)</span>
            </div>
            <div className="text-[11px] font-mono text-zinc-300">
              Status: {health ? health.database.status : "Probing..."}
            </div>
            <p className="text-[11px] text-zinc-500">
              Target: Supabase PostgreSQL with pgvector extension
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-zinc-400">
              <Shield className="h-4 w-4" />
              <span className="font-medium">Identity Provider</span>
            </div>
            <div className="text-[11px] font-mono text-zinc-300">
              Provider: {health ? health.auth.provider : "supabase"}
            </div>
            <p className="text-[11px] text-zinc-500">
              State: {health?.auth.configured ? "Configured" : "Unconfigured (Local fallback)"}
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-2">
            <div className="flex items-center space-x-2 text-zinc-400">
              <Cpu className="h-4 w-4" />
              <span className="font-medium">AI Abstraction Architecture</span>
            </div>
            <div className="text-[11px] font-mono text-zinc-300">
              Configured for Phase 3
            </div>
            <p className="text-[11px] text-zinc-500">
              Replaceable LLM & Embedding provider adapters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
