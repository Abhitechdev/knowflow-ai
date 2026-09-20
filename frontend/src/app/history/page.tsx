"use client";

import { History, AlertCircle, Clock } from "lucide-react";

export default function HistoryPage() {
  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl font-semibold tracking-tight text-white">Conversation History</h1>
          <span className="rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-medium text-amber-400">
            Phase 4 Milestone
          </span>
        </div>
        <p className="text-xs text-zinc-400 mt-1">
          Review past knowledge queries, citations, and verified evidence threads.
        </p>
      </div>

      {/* Phase Notice */}
      <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h2 className="text-xs font-semibold text-amber-300">History Persistence in Phase 3 & 4</h2>
            <p className="text-xs leading-relaxed text-amber-400/80">
              Conversations, messages, and message sources will be stored in PostgreSQL under the `conversations` table.
              Users can reopen previous answers and examine historical citations.
            </p>
          </div>
        </div>
      </div>

      {/* Empty State */}
      <div className="rounded-2xl border border-zinc-800/80 bg-zinc-950/40 p-12 text-center space-y-3">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-zinc-800 bg-zinc-900 text-zinc-500">
          <Clock className="h-6 w-6" />
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-semibold text-zinc-200">No Historical Sessions</h3>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto leading-relaxed">
            Your prior knowledge inquiries, answers, and citation trails will be preserved here once the RAG pipeline is active.
          </p>
        </div>
        <div className="pt-2 flex justify-center items-center space-x-2 text-[11px] text-zinc-500">
          <History className="h-3.5 w-3.5" />
          <span>PostgreSQL `conversations` + `messages` tables</span>
        </div>
      </div>
    </div>
  );
}
