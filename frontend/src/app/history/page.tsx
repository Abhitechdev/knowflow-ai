"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { History, Clock, MessageSquare, Trash2, Loader2, ArrowRight } from "lucide-react";
import { fetchConversations, deleteConversation, ConversationSummary } from "@/lib/api";

export default function HistoryPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetchConversations();
      setConversations(res.data || []);
    } catch (err: any) {
      setError(err.message || "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch (err: any) {
      alert("Failed to delete conversation: " + err.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-text-primary flex items-center gap-2">
          <History className="h-5 w-5 text-accent" />
          Conversation History
        </h1>
        <p className="text-xs text-text-muted mt-1">
          Review your past knowledge queries and citation trails.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-danger/20 bg-danger/10 p-4 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-text-muted" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="rounded-2xl border border-border bg-surface-muted p-12 text-center space-y-3">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-surface text-text-muted">
              <Clock className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-text-primary">No Historical Sessions</h3>
              <p className="text-xs text-text-muted max-w-sm mx-auto leading-relaxed">
                Your past interactions with the AI will appear here. Start a new chat to begin.
              </p>
            </div>
            <Link
              href="/chat"
              className="mt-4 inline-flex items-center space-x-2 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-white hover:bg-accent-hover transition-colors"
            >
              <span>Ask AI</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        ) : (
          <div className="grid gap-3">
            {conversations.map((conv) => (
              <Link
                key={conv.id}
                href={`/chat?q=&id=${conv.id}`} // assuming chat handles it via selection in side bar, but just linking
                className="group flex items-center justify-between rounded-xl border border-border bg-surface-muted p-4 hover:border-border-hover hover:bg-surface-hover transition-all"
              >
                <div className="flex items-start space-x-4">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface text-text-muted">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors">
                      {conv.title}
                    </h3>
                    <div className="mt-1 flex items-center space-x-2 text-xs text-text-muted">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{new Date(conv.updated_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={(e) => handleDelete(conv.id, e)}
                    className="p-2 text-text-muted hover:text-danger hover:bg-surface rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                    title="Delete Conversation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                  <ArrowRight className="h-4 w-4 text-text-muted group-hover:text-accent transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
