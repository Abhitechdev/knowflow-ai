"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { SystemHealthBadge } from "@/components/system-health-badge";
import {
  FileText,
  Bot,
  Search,
  MessageSquare,
  History,
  ArrowRight,
  Clock,
} from "lucide-react";
import { fetchConversations, ConversationSummary } from "@/lib/api";

export default function DashboardPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const convs = await fetchConversations();
        setConversations((convs.data || []).slice(0, 5)); // Show max 5 recent
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Welcome Banner */}
      <div className="rounded-2xl border border-border bg-surface p-6 sm:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-text-primary">
              Welcome to KnowFlow AI
            </h1>
            <p className="text-sm text-text-muted max-w-2xl leading-relaxed">
              Your enterprise knowledge assistant. Ask grounded questions based on company SOPs and documentation.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 gap-4">
            <Link
              href="/chat"
              className="group rounded-xl border border-border bg-surface-muted p-5 flex items-center justify-between hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface text-accent">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-medium text-text-primary">Ask AI</h3>
                  <p className="text-xs text-text-muted">Query your company knowledge base</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-text-muted group-hover:text-accent transition-colors" />
            </Link>

            <Link
              href="/documents"
              className="group rounded-xl border border-border bg-surface-muted p-5 flex items-center justify-between hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface text-accent">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-medium text-text-primary">Upload Documents</h3>
                  <p className="text-xs text-text-muted">Add new SOPs and manuals</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-text-muted group-hover:text-accent transition-colors" />
            </Link>

            <Link
              href="/search"
              className="group rounded-xl border border-border bg-surface-muted p-5 flex items-center justify-between hover:bg-surface-hover transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface text-accent">
                  <Search className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-medium text-text-primary">Search Knowledge</h3>
                  <p className="text-xs text-text-muted">Find specific document sections</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-text-muted group-hover:text-accent transition-colors" />
            </Link>
          </div>
        </div>

        {/* Recent Conversations */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
              <History className="h-5 w-5 text-text-muted" />
              Recent Conversations
            </h2>
            <Link href="/history" className="text-xs text-accent hover:underline">
              View all
            </Link>
          </div>
          
          <div className="rounded-xl border border-border bg-surface-muted overflow-hidden">
            {loading ? (
              <div className="p-6 flex justify-center space-x-2">
                <div className="h-2 w-2 bg-text-muted rounded-full animate-bounce"></div>
                <div className="h-2 w-2 bg-text-muted rounded-full animate-bounce delay-75"></div>
                <div className="h-2 w-2 bg-text-muted rounded-full animate-bounce delay-150"></div>
              </div>
            ) : conversations.length > 0 ? (
              <div className="divide-y divide-border">
                {conversations.map((conv) => (
                  <Link
                    key={conv.id}
                    href={`/chat?id=${conv.id}`}
                    className="block p-4 hover:bg-surface-hover transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <MessageSquare className="h-4 w-4 text-text-muted shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-text-primary truncate">
                          {conv.title}
                        </p>
                        <p className="text-xs text-text-muted mt-0.5 flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(conv.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-surface mb-3 border border-border">
                  <MessageSquare className="h-6 w-6 text-text-muted" />
                </div>
                <h3 className="text-sm font-medium text-text-primary">No conversations yet</h3>
                <p className="text-xs text-text-muted mt-1">
                  Start asking questions to see your history here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
