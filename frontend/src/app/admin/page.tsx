"use client";

import { useEffect, useState } from "react";
import {
  AdminStats,
  AuditLogRecord,
  EvaluationSummary,
  fetchAdminStats,
  fetchAuditLogs,
  triggerEvaluationBenchmark,
} from "@/lib/api";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<"evaluation" | "stats" | "audit">("evaluation");
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogRecord[]>([]);
  const [auditFilter, setAuditFilter] = useState<string>("");
  const [evalSummary, setEvalSummary] = useState<EvaluationSummary | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInitialData() {
      const [statsRes, logsRes] = await Promise.all([
        fetchAdminStats(),
        fetchAuditLogs(),
      ]);
      if (statsRes.data) setStats(statsRes.data);
      if (logsRes.data) setAuditLogs(logsRes.data);
    }
    loadInitialData();
  }, []);

  async function handleRunEvaluation() {
    setIsEvaluating(true);
    setEvalError(null);
    const res = await triggerEvaluationBenchmark();
    if (res.data) {
      setEvalSummary(res.data);
    } else {
      setEvalError(res.error || "Failed to execute evaluation benchmark.");
    }
    setIsEvaluating(false);
  }

  async function handleFilterAudit(action: string) {
    setAuditFilter(action);
    const res = await fetchAuditLogs(action || undefined);
    if (res.data) setAuditLogs(res.data);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-border gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Production & Evaluation Center</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-success/10 text-success border border-success/30">
              Phase 4 Hardened
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Automated RAG evaluation benchmarks, retrieval ranking metrics, and auditability foundations.
          </p>
        </div>

        {/* Tab switcher */}
        <div className="flex bg-surface-muted p-1 rounded-xl border border-border text-sm font-medium">
          <button
            onClick={() => setActiveTab("evaluation")}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === "evaluation"
                ? "bg-accent text-white shadow-sm"
                : "text-text-muted hover:text-text-primary hover:bg-surface-hover"
            }`}
          >
            RAG Evaluation
          </button>
          <button
            onClick={() => setActiveTab("stats")}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === "stats"
                ? "bg-accent text-white shadow-sm"
                : "text-text-muted hover:text-text-primary hover:bg-surface-hover"
            }`}
          >
            System Metrics
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === "audit"
                ? "bg-accent text-white shadow-sm"
                : "text-text-muted hover:text-text-primary hover:bg-surface-hover"
            }`}
          >
            Audit Trails
          </button>
        </div>
      </div>

      {/* Tab 1: RAG Evaluation Benchmark */}
      {activeTab === "evaluation" && (
        <div className="mt-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-surface-muted border border-border">
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Automated Golden Benchmark Test Suite</h2>
              <p className="text-xs text-text-muted mt-0.5">
                Executes verified SOP test cases (Cold Chain, Deviations, IT Security, HR) and adversarial out-of-scope queries.
              </p>
            </div>
            <button
              onClick={handleRunEvaluation}
              disabled={isEvaluating}
              className="px-5 py-2.5 rounded-xl bg-accent hover:bg-accent-hover text-white text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {isEvaluating ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Running Benchmark...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Run Benchmark Evaluation
                </>
              )}
            </button>
          </div>

          {evalError && (
            <div className="p-4 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm">
              {evalError}
            </div>
          )}

          {evalSummary && (
            <div className="space-y-6">
              {/* Primary Score Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">Pass Rate</span>
                  <div className="text-2xl font-bold text-success mt-1">{evalSummary.pass_rate_pct}%</div>
                  <span className="text-[11px] text-text-muted">{evalSummary.passed_cases}/{evalSummary.total_cases} passed</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">Hit Rate @ 1</span>
                  <div className="text-2xl font-bold text-text-primary mt-1">{(evalSummary.hit_rate_at_1 * 100).toFixed(1)}%</div>
                  <span className="text-[11px] text-text-muted">Top-1 rank match</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">Hit Rate @ 3</span>
                  <div className="text-2xl font-bold text-text-primary mt-1">{(evalSummary.hit_rate_at_3 * 100).toFixed(1)}%</div>
                  <span className="text-[11px] text-text-muted">Top-3 recall</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">MRR</span>
                  <div className="text-2xl font-bold text-accent mt-1">{evalSummary.mrr.toFixed(3)}</div>
                  <span className="text-[11px] text-text-muted">Mean Recip. Rank</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">NDCG @ 5</span>
                  <div className="text-2xl font-bold text-accent mt-1">{evalSummary.ndcg_at_5.toFixed(3)}</div>
                  <span className="text-[11px] text-text-muted">Ranking gain</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">Faithfulness</span>
                  <div className="text-2xl font-bold text-success mt-1">{(evalSummary.avg_faithfulness * 100).toFixed(1)}%</div>
                  <span className="text-[11px] text-text-muted">Evidence entailment</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border">
                  <span className="text-xs text-text-muted font-medium">Avg Latency</span>
                  <div className="text-2xl font-bold text-warning mt-1">{evalSummary.avg_latency_ms}ms</div>
                  <span className="text-[11px] text-text-muted">Per query pipeline</span>
                </div>
              </div>

              {/* Classification Error Reporting (Separate FP & FN) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-success/10 border border-success/20 flex items-center justify-between">
                  <div>
                    <div className="text-xs text-success font-semibold uppercase tracking-wider">Refusal Accuracy</div>
                    <div className="text-xl font-bold text-text-primary mt-1">{evalSummary.refusal_accuracy_pct}%</div>
                    <p className="text-xs text-text-muted mt-0.5">Out-of-scope query defense</p>
                  </div>
                  <span className="text-2xl">🛡️</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border flex items-center justify-between">
                  <div>
                    <div className="text-xs text-text-muted font-semibold uppercase tracking-wider">False Positives</div>
                    <div className="text-xl font-bold text-text-primary mt-1">{evalSummary.false_positives}</div>
                    <p className="text-xs text-text-muted mt-0.5">Valid SOP questions refused erroneously</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded font-bold ${evalSummary.false_positives === 0 ? "bg-success/20 text-success" : "bg-danger/20 text-danger"}`}>
                    {evalSummary.false_positives === 0 ? "0 (Optimal)" : `${evalSummary.false_positives} Refusals`}
                  </span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border flex items-center justify-between">
                  <div>
                    <div className="text-xs text-text-muted font-semibold uppercase tracking-wider">False Negatives</div>
                    <div className="text-xl font-bold text-text-primary mt-1">{evalSummary.false_negatives}</div>
                    <p className="text-xs text-text-muted mt-0.5">Out-of-scope questions answered (hallucination)</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded font-bold ${evalSummary.false_negatives === 0 ? "bg-success/20 text-success" : "bg-danger/20 text-danger"}`}>
                    {evalSummary.false_negatives === 0 ? "0 (Zero Hallucination)" : `${evalSummary.false_negatives} Leaks`}
                  </span>
                </div>
              </div>

              {/* Per-Case Details Table */}
              <div className="bg-surface rounded-2xl border border-border overflow-hidden">
                <div className="px-5 py-3.5 border-b border-border flex items-center justify-between bg-surface-muted">
                  <h3 className="text-sm font-semibold text-text-primary">Detailed Case-by-Case Benchmark Results</h3>
                  <span className="text-xs text-text-muted">{evalSummary.case_results.length} Test Vectors Evaluated</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-surface-muted text-text-muted uppercase tracking-wider border-b border-border">
                      <tr>
                        <th className="px-4 py-3">Case ID</th>
                        <th className="px-4 py-3">Question</th>
                        <th className="px-4 py-3">Category</th>
                        <th className="px-4 py-3">Hit @ 3</th>
                        <th className="px-4 py-3">MRR</th>
                        <th className="px-4 py-3">Faithfulness</th>
                        <th className="px-4 py-3">Latency</th>
                        <th className="px-4 py-3 text-right">Result</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border text-text-primary">
                      {evalSummary.case_results.map((c) => (
                        <tr key={c.case_id} className="hover:bg-surface-hover transition-colors">
                          <td className="px-4 py-3 font-mono text-text-muted">{c.case_id}</td>
                          <td className="px-4 py-3 max-w-xs truncate text-text-primary font-medium">{c.question}</td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-surface-muted text-text-muted border border-border">
                              {c.category}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-mono">{c.is_out_of_scope ? "N/A" : c.hit_at_3.toFixed(1)}</td>
                          <td className="px-4 py-3 font-mono">{c.is_out_of_scope ? "N/A" : c.mrr.toFixed(2)}</td>
                          <td className="px-4 py-3 font-mono">
                            {c.is_out_of_scope ? (
                              <span className="text-success">Refused</span>
                            ) : (
                              `${(c.faithfulness_score * 100).toFixed(0)}%`
                            )}
                          </td>
                          <td className="px-4 py-3 font-mono text-text-muted">{c.latency_ms}ms</td>
                          <td className="px-4 py-3 text-right">
                            <span
                              className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                                c.passed
                                  ? "bg-success/10 text-success border border-success/30"
                                  : "bg-danger/10 text-danger border border-danger/30"
                              }`}
                            >
                              {c.passed ? "PASS" : "FAIL"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: System Stats & Latency Telemetry */}
      {activeTab === "stats" && stats && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-surface border border-border">
              <span className="text-xs text-text-muted font-medium">Ingested Documents</span>
              <div className="text-3xl font-bold text-text-primary mt-1">{stats.total_documents}</div>
              <span className="text-xs text-text-muted">{stats.total_chunks} total chunks indexed</span>
            </div>
            <div className="p-5 rounded-2xl bg-surface border border-border">
              <span className="text-xs text-text-muted font-medium">Conversations</span>
              <div className="text-3xl font-bold text-text-primary mt-1">{stats.total_conversations}</div>
              <span className="text-xs text-text-muted">{stats.total_messages} messages recorded</span>
            </div>
            <div className="p-5 rounded-2xl bg-surface border border-border">
              <span className="text-xs text-text-muted font-medium">Audit Events</span>
              <div className="text-3xl font-bold text-accent mt-1">{stats.total_audit_events}</div>
              <span className="text-xs text-text-muted">Auditability records in DB</span>
            </div>
            <div className="p-5 rounded-2xl bg-surface border border-border">
              <span className="text-xs text-text-muted font-medium">User Feedback Ratio</span>
              <div className="text-3xl font-bold text-success mt-1">
                +{stats.positive_feedback_count} / -{stats.negative_feedback_count}
              </div>
              <span className="text-xs text-text-muted">Thumbs up / down</span>
            </div>
          </div>

          {/* Hardening Status */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
            <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">Production Engine Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-surface-muted border border-border space-y-1">
                <span className="text-text-muted">Grounded Answering Policy</span>
                <div className="text-success font-bold text-sm">ENFORCED (Server-Side)</div>
                <p className="text-text-muted">Refuses answers when evidence density is below safety threshold.</p>
              </div>
              <div className="p-4 rounded-xl bg-surface-muted border border-border space-y-1">
                <span className="text-text-muted">Stage 2 Reranking</span>
                <div className="text-accent font-bold text-sm">HYBRID RERANKER</div>
                <p className="text-text-muted">Continuous phrase, spec density, and heading alignment.</p>
              </div>
              <div className="p-4 rounded-xl bg-surface-muted border border-border space-y-1">
                <span className="text-text-muted">Security Guardrails</span>
                <div className="text-accent font-bold text-sm">ACTIVE</div>
                <p className="text-text-muted">Prompt injection filter, XML boundary isolation, rate limiter.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Audit Trails */}
      {activeTab === "audit" && (
        <div className="mt-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Auditability Trails</h2>
              <p className="text-xs text-text-muted">
                Auditability foundations relevant to regulated environments (queries, denials, alerts).
              </p>
            </div>
            <div className="flex gap-2">
              {["", "QUESTION_ASKED", "SECURITY_ALERT", "ACCESS_DENIED"].map((act) => (
                <button
                  key={act}
                  onClick={() => handleFilterAudit(act)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    auditFilter === act
                      ? "bg-accent text-white"
                      : "bg-surface-muted text-text-muted hover:text-text-primary border border-border"
                  }`}
                >
                  {act === "" ? "All Events" : act}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-surface rounded-2xl border border-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-muted text-text-muted uppercase tracking-wider border-b border-border">
                  <tr>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3">Action</th>
                    <th className="px-4 py-3">User ID</th>
                    <th className="px-4 py-3">IP Address</th>
                    <th className="px-4 py-3">Metadata</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border text-text-primary">
                  {auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                        No audit events recorded yet.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-surface-hover">
                        <td className="px-4 py-3 font-mono text-text-muted">{log.created_at.slice(0, 19)}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              log.action === "SECURITY_ALERT"
                                ? "bg-danger/10 text-danger border border-danger/30"
                                : log.action === "ACCESS_DENIED"
                                ? "bg-warning/10 text-warning border border-warning/30"
                                : "bg-accent/10 text-accent border border-accent/30"
                            }`}
                          >
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-text-muted">{log.user_id || "Anonymous"}</td>
                        <td className="px-4 py-3 font-mono text-text-muted">{log.ip_address || "Internal"}</td>
                        <td className="px-4 py-3 font-mono text-text-muted max-w-md truncate">{log.metadata_json}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
