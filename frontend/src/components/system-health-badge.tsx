"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth, HealthData } from "@/lib/api";
import { Activity, AlertCircle, RefreshCw, Database, Shield, Server } from "lucide-react";

export function SystemHealthBadge() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const checkHealth = async () => {
    setLoading(true);
    const res = await fetchSystemHealth();
    setHealth(res.data);
    setError(res.error);
    setLatency(res.latencyMs);
    setLoading(false);
  };

  useEffect(() => {
    checkHealth();
    // Recheck every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-zinc-800/60 pb-4">
        <div className="flex items-center space-x-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300">
            <Activity className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-zinc-100">Backend Connectivity</h3>
            <p className="text-xs text-zinc-400">Live probe to FastAPI /api/health</p>
          </div>
        </div>

        <button
          onClick={checkHealth}
          disabled={loading}
          className="inline-flex items-center space-x-1.5 rounded-md border border-zinc-700 bg-zinc-800/80 px-2.5 py-1 text-xs font-medium text-zinc-200 transition-colors hover:bg-zinc-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          <span>{loading ? "Probing..." : "Test Probe"}</span>
        </button>
      </div>

      {loading && !health && !error ? (
        <div className="py-6 text-center text-xs text-zinc-400 animate-pulse">
          Connecting to backend service...
        </div>
      ) : error ? (
        <div className="mt-4 rounded-lg border border-red-500/20 bg-red-950/20 p-3.5">
          <div className="flex items-start space-x-2.5">
            <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 shrink-0" />
            <div>
              <p className="text-xs font-semibold text-red-300">Connection Failed</p>
              <p className="text-xs text-red-400/90 mt-0.5">{error}</p>
              <p className="text-[11px] text-zinc-400 mt-1.5">
                Ensure the FastAPI backend is running on <code>http://localhost:8000</code>.
              </p>
            </div>
          </div>
        </div>
      ) : health ? (
        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {/* API Health */}
            <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/40 p-3">
              <div className="flex items-center space-x-2 text-zinc-400">
                <Server className="h-3.5 w-3.5" />
                <span className="text-[11px] font-medium uppercase tracking-wider">FastAPI Core</span>
              </div>
              <div className="mt-2 flex items-center space-x-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wide">
                  {health.status}
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">
                v{health.version} • {latency}ms latency
              </p>
            </div>

            {/* Database Health */}
            <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/40 p-3">
              <div className="flex items-center space-x-2 text-zinc-400">
                <Database className="h-3.5 w-3.5" />
                <span className="text-[11px] font-medium uppercase tracking-wider">Database</span>
              </div>
              <div className="mt-2 flex items-center space-x-2">
                <span
                  className={`flex h-2 w-2 rounded-full ${
                    health.database.connected
                      ? "bg-emerald-400"
                      : health.database.status === "unconfigured"
                      ? "bg-amber-400"
                      : "bg-red-400"
                  }`}
                />
                <span
                  className={`text-xs font-semibold uppercase tracking-wide ${
                    health.database.connected
                      ? "text-emerald-400"
                      : health.database.status === "unconfigured"
                      ? "text-amber-400"
                      : "text-red-400"
                  }`}
                >
                  {health.database.status}
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1 truncate" title={health.database.message}>
                {health.database.message || "PostgreSQL target"}
              </p>
            </div>

            {/* Auth Provider */}
            <div className="rounded-lg border border-zinc-800/80 bg-zinc-950/40 p-3">
              <div className="flex items-center space-x-2 text-zinc-400">
                <Shield className="h-3.5 w-3.5" />
                <span className="text-[11px] font-medium uppercase tracking-wider">Auth Provider</span>
              </div>
              <div className="mt-2 flex items-center space-x-2">
                <span
                  className={`flex h-2 w-2 rounded-full ${
                    health.auth.configured ? "bg-emerald-400" : "bg-amber-400"
                  }`}
                />
                <span
                  className={`text-xs font-semibold uppercase tracking-wide ${
                    health.auth.configured ? "text-emerald-400" : "text-amber-400"
                  }`}
                >
                  {health.auth.configured ? "Configured" : "Unconfigured"}
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 mt-1 truncate">
                {health.auth.provider} adapter
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-1">
            <span>Environment: <strong className="text-zinc-400 font-mono">{health.environment}</strong></span>
            <span>Last Probe: {new Date(health.timestamp).toLocaleTimeString()}</span>
          </div>
        </div>
      ) : null}
    </div>
  );
}
