"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth, HealthData } from "@/lib/api";
import { Activity, RefreshCw } from "lucide-react";

export function BackendStatusIndicator({ compact = false }: { compact?: boolean }) {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [statusText, setStatusText] = useState<"CHECKING" | "CONNECTED" | "DEGRADED" | "UNAVAILABLE">("CHECKING");

  const probe = async () => {
    setStatusText("CHECKING");
    const res = await fetchSystemHealth();
    if (res.data) {
      setHealth(res.data);
      setError(null);
      setLatency(res.latencyMs);
      if (res.data.status === "healthy") {
        setStatusText("CONNECTED");
      } else {
        setStatusText("DEGRADED");
      }
    } else {
      setHealth(null);
      setError(res.error);
      setLatency(res.latencyMs);
      setStatusText("UNAVAILABLE");
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
            statusText === "CONNECTED"
              ? "bg-success"
              : statusText === "DEGRADED"
              ? "bg-warning"
              : statusText === "CHECKING"
              ? "bg-text-muted animate-pulse"
              : "bg-danger"
          }`}
        />
        <span
          className={`text-xs font-medium ${
            statusText === "CONNECTED"
              ? "text-success"
              : statusText === "DEGRADED"
              ? "text-warning"
              : statusText === "CHECKING"
              ? "text-text-muted"
              : "text-danger"
          }`}
        >
          {statusText}
        </span>
        {latency !== null && (statusText === "CONNECTED" || statusText === "DEGRADED") && (
          <span className="text-[10px] text-text-muted font-mono">({latency}ms)</span>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-3 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="h-3.5 w-3.5 text-text-muted" />
          <span className="font-medium text-text-primary">FastAPI Backend</span>
        </div>
        <button
          onClick={probe}
          title="Re-check health"
          className="text-text-muted hover:text-text-primary transition-colors p-1"
        >
          <RefreshCw className={`h-3 w-3 ${statusText === "CHECKING" ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="mt-2 flex items-center space-x-2">
        <span
          className={`h-2 w-2 rounded-full ${
            statusText === "CONNECTED"
              ? "bg-success"
              : statusText === "DEGRADED"
              ? "bg-warning"
              : statusText === "CHECKING"
              ? "bg-text-muted animate-pulse"
              : "bg-danger"
          }`}
        />
        <span
          className={`font-semibold tracking-wide ${
            statusText === "CONNECTED"
              ? "text-success"
              : statusText === "DEGRADED"
              ? "text-warning"
              : statusText === "CHECKING"
              ? "text-text-muted"
              : "text-danger"
          }`}
        >
          {statusText}
        </span>
        {latency !== null && (statusText === "CONNECTED" || statusText === "DEGRADED") && (
          <span className="text-[11px] text-text-muted font-mono">{latency}ms</span>
        )}
      </div>

      {statusText === "UNAVAILABLE" && error && (
        <p className="mt-1.5 text-[11px] text-danger leading-tight">
          {error}
        </p>
      )}

      {health && (
        <div className="mt-2 pt-2 border-t border-border space-y-1 text-[11px] text-text-muted">
          <div className="flex justify-between">
            <span>Database:</span>
            <span
              className={`font-mono ${
                health.database.connected
                  ? "text-success"
                  : health.database.status === "unconfigured"
                  ? "text-warning"
                  : "text-danger"
              }`}
            >
              {health.database.status}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Auth:</span>
            <span className="font-mono text-text-primary">
              {health.auth.configured ? "configured" : "unconfigured"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
