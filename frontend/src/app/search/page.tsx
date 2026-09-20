"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  SlidersHorizontal,
  FileText,
  ArrowRight,
  Clock,
  AlertCircle,
} from "lucide-react";
import { performHybridSearch, SearchChunkResult } from "@/lib/api";

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchChunkResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const q = query.trim();
    if (!q) return;

    setLoading(true);
    setErrorMsg(null);
    const res = await performHybridSearch({
      query: q,
      top_k: 8,
    });

    if (res.error) {
      setErrorMsg(res.error);
      setResults([]);
    } else if (res.data) {
      setResults(res.data.results);
      setLatencyMs(res.data.latency_ms);
    }
    setSearched(true);
    setLoading(false);
  };

  const handleAskAI = () => {
    router.push(`/chat?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl font-semibold tracking-tight text-white">Knowledge Base Search</h1>
          <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-medium text-emerald-400">
            Hybrid RRF Live
          </span>
        </div>
        <p className="text-xs text-zinc-400 mt-1">
          Dense vector similarity (384-dim embeddings) fused with sparse BM25 keyword matching across authorized SOPs.
        </p>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="relative">
          <Search className="absolute left-4 top-3.5 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search procedures, cold chain limits, deviation timelines, password rules..."
            className="w-full rounded-xl border border-zinc-800 bg-zinc-900/60 py-3 pl-11 pr-24 text-xs text-zinc-100 placeholder-zinc-500 focus:border-indigo-500/60 focus:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-indigo-500/30"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 top-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Filter Chips & Stats */}
        <div className="flex items-center justify-between text-xs text-zinc-400">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="h-3.5 w-3.5 text-zinc-500" />
            <span className="text-[11px] text-zinc-500">Quick Filters:</span>
            <button
              type="button"
              onClick={() => {
                setQuery("deviation management reporting timeline");
                setSearched(false);
              }}
              className="rounded-md border border-zinc-800 bg-zinc-900/60 px-2 py-0.5 text-[11px] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
            >
              Deviation SOP
            </button>
            <button
              type="button"
              onClick={() => {
                setQuery("refrigerated storage temperature limits");
                setSearched(false);
              }}
              className="rounded-md border border-zinc-800 bg-zinc-900/60 px-2 py-0.5 text-[11px] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
            >
              Cold Chain Limits
            </button>
            <button
              type="button"
              onClick={() => {
                setQuery("password complexity requirements");
                setSearched(false);
              }}
              className="rounded-md border border-zinc-800 bg-zinc-900/60 px-2 py-0.5 text-[11px] text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
            >
              Password Policy
            </button>
          </div>

          {latencyMs !== null && (
            <div className="flex items-center space-x-1.5 text-[11px] text-zinc-500">
              <Clock className="h-3 w-3" />
              <span>{latencyMs}ms</span>
              <span>·</span>
              <span>{results.length} results</span>
            </div>
          )}
        </div>
      </form>

      {/* Error state */}
      {errorMsg && (
        <div className="flex items-center space-x-2 rounded-xl border border-red-500/20 bg-red-950/20 p-3 text-xs text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Search Results */}
      {searched && (
        <div className="space-y-3">
          {results.length === 0 ? (
            <div className="rounded-2xl border border-zinc-800/80 bg-zinc-950/40 p-12 text-center space-y-2">
              <p className="text-sm font-semibold text-zinc-200">No matching documents found</p>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                No authorized company documentation in your workspace matched this query with sufficient relevance.
              </p>
            </div>
          ) : (
            results.map((r, idx) => (
              <div
                key={r.chunk_id || idx}
                className="group rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-4 transition-all hover:border-zinc-700 hover:bg-zinc-900/30 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded bg-indigo-950/50 text-indigo-400 border border-indigo-500/20">
                      <FileText className="h-3.5 w-3.5" />
                    </div>
                    <span className="text-xs font-semibold text-zinc-100">{r.document_title}</span>
                    <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400">
                      Page {r.page_number}
                    </span>
                    {r.section_heading && (
                      <span className="rounded bg-zinc-800/60 px-1.5 py-0.5 text-[10px] text-zinc-400 truncate max-w-xs">
                        {r.section_heading}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
                      {r.relevance_pct}% match
                    </span>
                    <button
                      onClick={() => handleAskAI()}
                      className="opacity-0 group-hover:opacity-100 flex items-center space-x-1 text-[11px] text-indigo-400 hover:text-indigo-300 transition-opacity"
                    >
                      <span>Ask AI</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-zinc-300 leading-relaxed font-mono bg-zinc-900/40 p-2.5 rounded-lg border border-zinc-850">
                  {r.snippet}
                </p>

                <div className="flex items-center space-x-3 text-[10px] text-zinc-500">
                  <span>Dense Score: {r.dense_score.toFixed(3)}</span>
                  <span>·</span>
                  <span>Sparse Score: {r.sparse_score.toFixed(3)}</span>
                  <span>·</span>
                  <span>RRF Fusion: {r.rrf_score.toFixed(4)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Initial state guide */}
      {!searched && (
        <div className="rounded-2xl border border-zinc-800/80 bg-zinc-950/40 p-10 text-center space-y-3">
          <div className="flex h-10 w-10 mx-auto items-center justify-center rounded-xl border border-zinc-700/80 bg-zinc-900 text-indigo-400">
            <Search className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-semibold text-zinc-200">Unified Knowledge Search</h3>
          <p className="text-xs text-zinc-400 max-w-md mx-auto leading-relaxed">
            Type any procedure question or keyword above to find exact SOP sections, regulatory guidelines,
            and compliance protocols with page-level precision.
          </p>
        </div>
      )}
    </div>
  );
}
