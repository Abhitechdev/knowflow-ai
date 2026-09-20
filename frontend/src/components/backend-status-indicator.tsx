"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth, HealthData } from "@/lib/api";
import { Activity, RefreshCw } from "lucide-react";

export function BackendStatusIndicator({ compact = false }: { compact?: boolean }) {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [statusText, setStatusText] = useState<"Checking..." | "Backend Online" | "Backend Unavailable">("Checking...");

  const probe = async () => {
    setStatusText("Checking...");
    const res = await fetchSystemHealth();
    if (res.data) {
      setHealth(res.data);
      setError(null);
      setLatency(res.latencyMs);
      setStatusText("Backend Online");
    } else {
      setHealth(null);
      setError(res.error);
      setLatency(res.latencyMs);
      setStatusText("Backend Unavailable");
    }
  };

  useEffect(() => {
    probe();
    const interval = setInterval(probe, 30000);
    return () => clearInterval(interval);
  }, []);

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <span
          className={`h-2 w-2 rounded-full ${
            statusText === "Backend Online"
              ? "bg-emerald-400 animate-pulse"
              : statusText === "Checking..."
              ? "bg-amber-400 animate-ping"
              : "bg-red-400"
          }`}
        />
        <span
          className={`text-xs font-medium ${
            statusText === "Backend Online"
              ? "text-emerald-400"
              : statusText === "Checking..."
              ? "text-amber-400"
              : "text-red-400"
          }`}
        >
          {statusText}
        </span>
        {latency !== null && statusText === "Backend Online" && (
          <span className="text-[10px] text-zinc-500 font-mono">({latency}ms)</span>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-3 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="h-3.5 w-3.5 text-zinc-400" />
          <span className="font-medium text-zinc-300">FastAPI Backend</span>
        </div>
        <button
          onClick={probe}
          title="Re-check health"
          className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
        >
          <RefreshCw className={`h-3 w-3 ${statusText === "Checking..." ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="mt-2 flex items-center space-x-2">
        <span
          className={`h-2 w-2 rounded-full ${
            statusText === "Backend Online"
              ? "bg-emerald-400"
              : statusText === "Checking..."
              ? "bg-amber-400 animate-pulse"
              : "bg-red-400"
          }`}
        />
        <span
          className={`font-semibold tracking-wide ${
            statusText === "Backend Online"
              ? "text-emerald-400"
              : statusText === "Checking..."
              ? "text-amber-400"
              : "text-red-400"
          }`}
        >
          {statusText}
        </span>
        {latency !== null && (
          <span className="text-[11px] text-zinc-500 font-mono">{latency}ms</span>
        )}
      </div>

      {statusText === "Backend Unavailable" && error && (
        <p className="mt-1.5 text-[11px] text-red-400/90 leading-tight">
          {error}
        </p>
      )}

      {health && (
        <div className="mt-2 pt-2 border-t border-zinc-800/80 space-y-1 text-[11px] text-zinc-400">
          <div className="flex justify-between">
            <span>Database:</span>
            <span
              className={`font-mono ${
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
          <div className="flex justify-between">
            <span>Auth:</span>
            <span className="font-mono text-zinc-300">
              {health.auth.configured ? "configured" : "unconfigured"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
