"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { SystemHealthBadge } from "@/components/system-health-badge";
import {
  FileText,
  Bot,
  Search,
  MessageSquare,
  History,
  ArrowRight,
  Clock,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Scale,
  Sparkles,
  Zap,
  BookOpen,
  Database,
  Cpu,
  Layers,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { fetchConversations, ConversationSummary } from "@/lib/api";

export default function HomePage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const supabase = createClient();

  useEffect(() => {
    async function checkAuth() {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      if (user) {
        try {
          const convs = await fetchConversations();
          setConversations((convs.data || []).slice(0, 5));
        } catch (error) {
          console.error("Failed to fetch dashboard data:", error);
        }
      }
      setLoading(false);
    }
    checkAuth();
  }, [supabase.auth]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  // ====================================================
  // AUTHENTICATED DASHBOARD VIEW
  // ====================================================
  if (user) {
    return (
      <div className="space-y-8 max-w-5xl mx-auto py-4">
        {/* Welcome Banner */}
        <div className="rounded-2xl border border-border bg-surface p-6 sm:p-8 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded-full bg-success/10 border border-success/30 px-2.5 py-0.5 text-xs font-medium text-success">
                  <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                  Authenticated Enterprise Workspace
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-text-primary">
                Welcome to KnowFlow AI
              </h1>
              <p className="text-sm text-text-muted max-w-2xl leading-relaxed">
                Your enterprise knowledge assistant. Ask grounded questions based on company SOPs and documentation.
              </p>
            </div>
            <div className="shrink-0">
              <SystemHealthBadge />
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

          {/* Recent Activity */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                Recent Conversations
              </h2>
              <Link href="/history" className="text-xs font-medium text-accent hover:underline flex items-center gap-1">
                View all <ArrowRight className="h-3 w-3" />
              </Link>
            </div>

            <div className="rounded-xl border border-border bg-surface p-4">
              {conversations.length === 0 ? (
                <div className="text-center py-8 text-text-muted space-y-3">
                  <MessageSquare className="h-8 w-8 mx-auto text-text-muted opacity-40" />
                  <p className="text-xs">No conversations yet.</p>
                  <Link
                    href="/chat"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-accent hover:underline"
                  >
                    Start a new conversation <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {conversations.map((conv) => (
                    <Link
                      key={conv.id}
                      href={`/chat?id=${conv.id}`}
                      className="block py-3 hover:bg-surface-hover rounded-lg px-3 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-sm text-text-primary truncate max-w-[280px]">
                          {conv.title}
                        </span>
                        <span className="text-[11px] text-text-muted flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(conv.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ====================================================
  // PUBLIC MARKETING LANDING PAGE VIEW
  // ====================================================
  return (
    <div className="min-h-screen bg-background text-text-primary selection:bg-accent/20">
      {/* Public Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface-muted text-accent transition-transform group-hover:scale-105">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-text-primary">KnowFlow AI</span>
              <span className="hidden sm:inline-block ml-2 text-[10px] uppercase font-semibold text-text-muted px-2 py-0.5 rounded-full border border-border bg-surface-muted">
                Enterprise SOP Agent
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-6 text-xs font-medium text-text-secondary">
            <a href="#capabilities" className="hover:text-text-primary transition-colors">Capabilities</a>
            <a href="#architecture" className="hover:text-text-primary transition-colors">How it Works</a>
            <Link href="/security" className="hover:text-text-primary transition-colors flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-success" /> DPDP Act & Security
            </Link>
          </nav>

          <div className="flex items-center space-x-3">
            <Link
              href="/login"
              className="rounded-lg border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-accent px-4 py-1.5 text-xs font-medium text-accent-foreground hover:bg-accent/90 transition-colors shadow-sm"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-surface-muted/40 via-background to-background py-20 sm:py-28">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8 space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/5 px-4 py-1.5 text-xs font-medium text-text-primary">
            <Sparkles className="h-3.5 w-3.5 text-accent" />
            Deterministic RAG • Zero Hallucinations • DPDPA 2023 Aligned
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl text-text-primary leading-tight">
            Turn Company Documents into <br className="hidden sm:inline" />
            <span className="text-accent underline decoration-accent/30 decoration-wavy">
              Grounded, Verifiable Knowledge
            </span>
          </h1>

          <p className="text-base sm:text-xl text-text-muted max-w-3xl mx-auto leading-relaxed">
            KnowFlow AI is the enterprise SOP and compliance assistant that only answers with direct citations from your verified documentation. No hallucinations. No unverified assumptions.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-8 py-3.5 text-sm font-semibold text-accent-foreground hover:bg-accent/90 transition-all shadow-lg hover:shadow-accent/10"
            >
              Create Free Workspace <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/security"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-surface px-8 py-3.5 text-sm font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              <ShieldCheck className="h-4 w-4 text-success" /> Explore Security & DPDP Compliance
            </Link>
          </div>

          {/* Value Proof Badges */}
          <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-success" /> 100% Grounded
              </div>
              <p className="text-[11px] text-text-muted">Strict refusal policy prevents model guessing.</p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <Scale className="h-4 w-4 text-success" /> DPDP Act 2023
              </div>
              <p className="text-[11px] text-text-muted">Full statutory data principal rights & safeguards.</p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <Lock className="h-4 w-4 text-success" /> Zero AI Training
              </div>
              <p className="text-[11px] text-text-muted">Customer data is never used to train public LLMs.</p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-success" /> Verified Citations
              </div>
              <p className="text-[11px] text-text-muted">Direct page, heading & paragraph references.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Architecture Flow */}
      <section id="architecture" className="border-b border-border py-20 bg-surface/50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-accent">Technical Architecture</div>
            <h2 className="text-3xl font-bold tracking-tight text-text-primary">
              Deterministic Ingestion & Grounding Pipeline
            </h2>
            <p className="text-sm text-text-muted max-w-2xl mx-auto">
              How KnowFlow AI transforms unstructured corporate files into authoritative, cited intelligence.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="rounded-xl border border-border bg-surface p-6 space-y-3 relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent font-bold">1</div>
              <h3 className="font-semibold text-base text-text-primary">Multi-Tier Ingestion</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Ingests PDF, DOCX, Markdown, and TXT files. Splits text along section headings, tables, and page boundaries to prevent fragmented context.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3 relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent font-bold">2</div>
              <h3 className="font-semibold text-base text-text-primary">Hybrid Indexing</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Generates dense OpenAI vector embeddings stored in PostgreSQL pgvector (HNSW index) paired with sparse BM25 token indexing for exact keyword precision.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3 relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent font-bold">3</div>
              <h3 className="font-semibold text-base text-text-primary">Strict Reranking</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Retrieves candidates, enforces departmental clearance rules, and reranks chunks to isolate the highest-confidence evidence paragraphs.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3 relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent font-bold">4</div>
              <h3 className="font-semibold text-base text-text-primary">Grounded Synthesis</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Generates answers strictly constrained to evidence chunks with embedded source citations. Automatically triggers refusal if evidence is lacking.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Problem vs Solution Section */}
      <section id="capabilities" className="border-b border-border py-20 bg-background">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-accent">Enterprise Comparison</div>
            <h2 className="text-3xl font-bold tracking-tight text-text-primary">
              Why Generic LLMs Fail in Enterprise Ops
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Generic LLMs */}
            <div className="rounded-2xl border border-danger/30 bg-danger/5 p-8 space-y-6">
              <div className="flex items-center gap-2 text-danger font-bold text-lg">
                <ShieldAlert className="h-5 w-5" /> Generic LLMs & Chatbots
              </div>
              <ul className="space-y-3.5 text-xs text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-danger font-bold">✕</span>
                  <span><strong>Hallucinates facts:</strong> Generates plausible-sounding but fictitious procedure details when answers are unknown.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-danger font-bold">✕</span>
                  <span><strong>No audit trail:</strong> Cannot link answers to specific page numbers or authorized revision dates.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-danger font-bold">✕</span>
                  <span><strong>Data privacy risk:</strong> Corporate prompts and secrets may be reused for public AI training cycles.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-danger font-bold">✕</span>
                  <span><strong>No clearance tiers:</strong> Internal documents are exposed indiscriminately without role-based access checks.</span>
                </li>
              </ul>
            </div>

            {/* KnowFlow AI */}
            <div className="rounded-2xl border border-success/30 bg-success/5 p-8 space-y-6">
              <div className="flex items-center gap-2 text-success font-bold text-lg">
                <ShieldCheck className="h-5 w-5" /> KnowFlow AI Enterprise
              </div>
              <ul className="space-y-3.5 text-xs text-text-secondary">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                  <span><strong>Grounded Answering Policy:</strong> Strictly constrained to retrieved chunks; transparently refuses if evidence is absent.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                  <span><strong>Deterministic Citations:</strong> Every assertion is linked to an exact document title, section heading, and page number.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                  <span><strong>DPDPA & GDPR Compliant:</strong> Customer data is isolated in private PostgreSQL partitions and never shared for model training.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                  <span><strong>Granular RBAC Clearance:</strong> Enforces Public, Internal, Confidential, and Restricted access boundaries.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-20 bg-gradient-to-t from-surface-muted/60 to-background">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8 space-y-6">
          <h2 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-text-primary">
            Ready to Empower Your Teams with Grounded Knowledge?
          </h2>
          <p className="text-sm text-text-muted max-w-xl mx-auto">
            Set up your organization&apos;s workspace in less than 2 minutes. Upload your SOPs and start querying with confidence.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-2">
            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-8 py-3.5 text-sm font-semibold text-accent-foreground hover:bg-accent/90 transition-all shadow-lg"
            >
              Get Started with KnowFlow <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-xl border border-border bg-surface px-8 py-3.5 text-sm font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              Sign In to Your Workspace
            </Link>
          </div>
        </div>
      </section>

      {/* Public Footer */}
      <footer className="border-t border-border bg-surface py-12 text-xs text-text-muted">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center space-x-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-md border border-border bg-surface-muted text-accent">
              <BookOpen className="h-4 w-4" />
            </div>
            <span className="font-semibold text-text-primary">KnowFlow AI</span>
            <span>&copy; 2026 KnowFlow AI. All rights reserved.</span>
          </div>

          <div className="flex flex-wrap items-center gap-6">
            <a href="#capabilities" className="hover:text-text-primary transition-colors">Capabilities</a>
            <a href="#architecture" className="hover:text-text-primary transition-colors">Architecture</a>
            <Link href="/security" className="hover:text-text-primary transition-colors flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-success" /> DPDP Act & Security
            </Link>
            <Link href="/login" className="hover:text-text-primary transition-colors">Sign In</Link>
            <Link href="/register" className="hover:text-text-primary transition-colors font-medium text-text-primary">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
