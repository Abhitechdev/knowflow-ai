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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

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
          <h1 className="text-xl font-semibold tracking-tight text-text-primary">Knowledge Base Search</h1>
          <span className="rounded-full border border-success/20 bg-success/10 px-2.5 py-0.5 text-[10px] font-medium text-success">
            Hybrid RRF Live
          </span>
        </div>
        <p className="text-xs text-text-muted mt-1">
          Dense vector similarity (384-dim embeddings) fused with sparse BM25 keyword matching across authorized SOPs.
        </p>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="relative flex items-center">
          <Search className="absolute left-4 h-4 w-4 text-text-muted" />
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search procedures, cold chain limits, deviation timelines, password rules..."
            className="w-full h-12 rounded-xl pl-11 pr-24 text-sm"
          />
          <Button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2"
            size="sm"
            loading={loading}
          >
            {!loading && "Search"}
          </Button>
        </div>

        {/* Filter Chips & Stats */}
        <div className="flex items-center justify-between text-xs text-text-muted">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span className="text-[11px]">Quick Filters:</span>
            <button
              type="button"
              onClick={() => {
                setQuery("deviation management reporting timeline");
                setSearched(false);
              }}
              className="rounded-md border border-border bg-surface-muted px-2 py-0.5 text-[11px] hover:border-border-hover hover:text-text-primary transition-colors"
            >
              Deviation SOP
            </button>
            <button
              type="button"
              onClick={() => {
                setQuery("refrigerated storage temperature limits");
                setSearched(false);
              }}
              className="rounded-md border border-border bg-surface-muted px-2 py-0.5 text-[11px] hover:border-border-hover hover:text-text-primary transition-colors"
            >
              Cold Chain Limits
            </button>
            <button
              type="button"
              onClick={() => {
                setQuery("password complexity requirements");
                setSearched(false);
              }}
              className="rounded-md border border-border bg-surface-muted px-2 py-0.5 text-[11px] hover:border-border-hover hover:text-text-primary transition-colors"
            >
              Password Policy
            </button>
          </div>

          {latencyMs !== null && (
            <div className="flex items-center space-x-1.5 text-[11px]">
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
        <div className="flex items-center space-x-2 rounded-xl border border-danger/20 bg-danger/10 p-3 text-xs text-danger">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Search Results */}
      {searched && (
        <div className="space-y-3">
          {results.length === 0 ? (
            <div className="rounded-2xl border border-border bg-surface-muted p-12 text-center space-y-2">
              <p className="text-sm font-semibold text-text-primary">No matching documents found</p>
              <p className="text-xs text-text-muted max-w-sm mx-auto">
                No authorized company documentation in your workspace matched this query with sufficient relevance.
              </p>
            </div>
          ) : (
            results.map((r, idx) => (
              <div
                key={r.chunk_id || idx}
                className="group rounded-xl border border-border bg-surface-muted p-4 transition-all hover:bg-surface-hover space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded bg-surface border border-border text-accent">
                      <FileText className="h-3.5 w-3.5" />
                    </div>
                    <span className="text-xs font-semibold text-text-primary">{r.document_title}</span>
                    <span className="rounded bg-surface px-1.5 py-0.5 text-[10px] text-text-muted border border-border">
                      Page {r.page_number}
                    </span>
                    {r.section_heading && (
                      <span className="rounded bg-surface px-1.5 py-0.5 text-[10px] text-text-muted border border-border truncate max-w-xs">
                        {r.section_heading}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="rounded-full border border-success/30 bg-success/10 px-2 py-0.5 text-[10px] font-medium text-success">
                      {r.relevance_pct}% match
                    </span>
                    <button
                      onClick={() => handleAskAI()}
                      className="opacity-0 group-hover:opacity-100 flex items-center space-x-1 text-[11px] text-accent hover:underline transition-opacity"
                    >
                      <span>Ask AI</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-text-primary leading-relaxed font-mono bg-surface p-2.5 rounded-lg border border-border">
                  {r.snippet}
                </p>

                <div className="flex items-center space-x-3 text-[10px] text-text-muted">
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
        <div className="rounded-2xl border border-border bg-surface-muted p-10 text-center space-y-3">
          <div className="flex h-10 w-10 mx-auto items-center justify-center rounded-xl border border-border bg-surface text-accent">
            <Search className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-semibold text-text-primary">Unified Knowledge Search</h3>
          <p className="text-xs text-text-muted max-w-md mx-auto leading-relaxed">
            Type any procedure question or keyword above to find exact SOP sections, regulatory guidelines,
            and compliance protocols with page-level precision.
          </p>
        </div>
      )}
    </div>
  );
}
