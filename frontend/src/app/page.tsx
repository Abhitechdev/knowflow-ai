"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
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
  BookOpen,
  Layers,
  Upload,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import {
  fetchConversations,
  fetchDocuments,
  ConversationSummary,
  DocumentItem,
} from "@/lib/api";

function getGreeting(email?: string | null): string {
  const hour = new Date().getHours();
  let timeGreeting = "Good morning";
  if (hour >= 12 && hour < 17) {
    timeGreeting = "Good afternoon";
  } else if (hour >= 17) {
    timeGreeting = "Good evening";
  }

  if (!email) return timeGreeting;
  const namePart = email.split("@")[0];
  const formattedName = namePart.charAt(0).toUpperCase() + namePart.slice(1);
  return `${timeGreeting}, ${formattedName}`;
}

export default function HomePage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const router = useRouter();
  const supabase = createClient();

  const loadWorkspaceData = async () => {
    setDataLoading(true);
    setFetchError(null);
    try {
      const [convsRes, docsRes] = await Promise.allSettled([
        fetchConversations(),
        fetchDocuments(),
      ]);

      if (convsRes.status === "fulfilled" && convsRes.value?.data) {
        setConversations(convsRes.value.data.slice(0, 5));
      }

      if (docsRes.status === "fulfilled" && docsRes.value?.items) {
        setDocuments(docsRes.value.items.slice(0, 5));
      }

      if (convsRes.status === "rejected" && docsRes.status === "rejected") {
        setFetchError("Some services are temporarily unavailable. Please try again.");
      }
    } catch (err) {
      setFetchError("Some services are temporarily unavailable. Please try again.");
    } finally {
      setDataLoading(false);
    }
  };

  useEffect(() => {
    // Check if landing with a password recovery token in URL hash
    if (typeof window !== "undefined" && window.location.hash.includes("type=recovery")) {
      router.push(`/update-password${window.location.hash}`);
      return;
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        router.push("/update-password");
      }
    });

    async function checkAuth() {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      setLoading(false);
      if (user) {
        loadWorkspaceData();
      }
    }
    checkAuth();

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase.auth, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  // ====================================================
  // AUTHENTICATED USER DASHBOARD
  // ====================================================
  if (user) {
    return (
      <div className="space-y-8 max-w-6xl mx-auto py-2">
        {/* Soft Error Banner if connectivity issue occurs */}
        {fetchError && (
          <div className="flex items-center justify-between rounded-xl border border-border bg-surface-muted p-4 text-xs text-text-secondary">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-warning" />
              <span>{fetchError}</span>
            </div>
            <button
              onClick={loadWorkspaceData}
              className="inline-flex items-center gap-1 font-medium text-accent hover:underline"
            >
              <RefreshCw className="h-3 w-3" /> Retry
            </button>
          </div>
        )}

        {/* User-Centric Hero Greeting */}
        <div className="rounded-2xl border border-border bg-surface p-6 sm:p-8 space-y-3">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
            {getGreeting(user.email)}
          </h1>
          <p className="text-sm text-text-muted max-w-2xl leading-relaxed">
            Search your organization&apos;s knowledge base, ask grounded questions, and review verified citations.
          </p>
        </div>

        {/* Primary Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Link
            href="/chat"
            className="group rounded-xl border border-border bg-surface p-5 flex flex-col justify-between hover:border-accent/40 hover:bg-surface-hover transition-all space-y-4"
          >
            <div className="space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-text-primary group-hover:text-accent transition-colors">
                  Ask AI
                </h3>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Ask questions about your organization&apos;s documents with verified citations.
                </p>
              </div>
            </div>
            <div className="inline-flex items-center text-xs font-medium text-accent gap-1">
              Start chat <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </Link>

          <Link
            href="/documents"
            className="group rounded-xl border border-border bg-surface p-5 flex flex-col justify-between hover:border-accent/40 hover:bg-surface-hover transition-all space-y-4"
          >
            <div className="space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent">
                <Upload className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-text-primary group-hover:text-accent transition-colors">
                  Upload Document
                </h3>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Add new SOPs, handbooks, and policy files to your knowledge base.
                </p>
              </div>
            </div>
            <div className="inline-flex items-center text-xs font-medium text-accent gap-1">
              Manage documents <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </Link>

          <Link
            href="/search"
            className="group rounded-xl border border-border bg-surface p-5 flex flex-col justify-between hover:border-accent/40 hover:bg-surface-hover transition-all space-y-4"
          >
            <div className="space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-muted text-accent">
                <Search className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-text-primary group-hover:text-accent transition-colors">
                  Search Knowledge
                </h3>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Find specific text excerpts across indexed corporate documents.
                </p>
              </div>
            </div>
            <div className="inline-flex items-center text-xs font-medium text-accent gap-1">
              Search passages <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </Link>
        </div>

        {/* Real Workspace Content: Recent Conversations & Documents */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Recent Conversations Card */}
          <div className="rounded-xl border border-border bg-surface p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-accent" />
                Recent Conversations
              </h2>
              {conversations.length > 0 && (
                <Link href="/history" className="text-xs font-medium text-accent hover:underline flex items-center gap-1">
                  View all <ArrowRight className="h-3 w-3" />
                </Link>
              )}
            </div>

            {dataLoading ? (
              <div className="space-y-3 py-2">
                <div className="h-10 rounded-lg bg-surface-muted animate-pulse" />
                <div className="h-10 rounded-lg bg-surface-muted animate-pulse" />
              </div>
            ) : conversations.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border p-6 text-center space-y-3">
                <p className="text-xs text-text-muted">No conversations yet</p>
                <Link
                  href="/chat"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-accent-foreground hover:bg-accent/90 transition-colors"
                >
                  <Bot className="h-3.5 w-3.5" /> Start a conversation
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {conversations.map((conv) => (
                  <Link
                    key={conv.id}
                    href={`/chat?id=${conv.id}`}
                    className="block py-2.5 hover:bg-surface-hover rounded-lg px-2 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-xs text-text-primary truncate max-w-[260px]">
                        {conv.title}
                      </span>
                      <span className="text-[11px] text-text-muted flex items-center gap-1 shrink-0">
                        <Clock className="h-3 w-3" />
                        {new Date(conv.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Indexed Documents Card */}
          <div className="rounded-xl border border-border bg-surface p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                <FileText className="h-4 w-4 text-accent" />
                Indexed Documents
              </h2>
              {documents.length > 0 && (
                <Link href="/documents" className="text-xs font-medium text-accent hover:underline flex items-center gap-1">
                  View all <ArrowRight className="h-3 w-3" />
                </Link>
              )}
            </div>

            {dataLoading ? (
              <div className="space-y-3 py-2">
                <div className="h-10 rounded-lg bg-surface-muted animate-pulse" />
                <div className="h-10 rounded-lg bg-surface-muted animate-pulse" />
              </div>
            ) : documents.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border p-6 text-center space-y-3">
                <p className="text-xs text-text-muted">No documents yet</p>
                <Link
                  href="/documents"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-accent-foreground hover:bg-accent/90 transition-colors"
                >
                  <Upload className="h-3.5 w-3.5" /> Upload your first document
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {documents.map((doc) => (
                  <Link
                    key={doc.id}
                    href="/documents"
                    className="block py-2.5 hover:bg-surface-hover rounded-lg px-2 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-xs text-text-primary truncate max-w-[260px]">
                        {doc.title || doc.original_filename}
                      </span>
                      <span className="text-[10px] rounded px-1.5 py-0.5 border border-border bg-surface-muted text-text-muted shrink-0 capitalize">
                        {doc.status.toLowerCase()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    );
  }

  // ====================================================
  // PUBLIC PRODUCT MARKETING LANDING PAGE
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
            Deterministic RAG • Grounded Answering • DPDPA 2023 & GDPR Aligned Controls
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
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-8 py-3.5 text-sm font-semibold text-accent-foreground hover:bg-accent/90 transition-all shadow-lg"
            >
              Create Free Workspace <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/security"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-surface px-8 py-3.5 text-sm font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              <ShieldCheck className="h-4 w-4 text-success" /> Explore Security & Privacy Controls
            </Link>
          </div>

          {/* Value Proof Badges */}
          <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-success" /> Grounded Citations
              </div>
              <p className="text-[11px] text-text-muted">Strict refusal policy prevents model guessing.</p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-4 space-y-1">
              <div className="font-semibold text-sm text-text-primary flex items-center gap-1.5">
                <Scale className="h-4 w-4 text-success" /> DPDP Act Controls
              </div>
              <p className="text-[11px] text-text-muted">Data principal rights and reasonable security safeguards.</p>
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

      {/* Enterprise Comparison */}
      <section id="capabilities" className="border-b border-border py-20 bg-background">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center space-y-3">
            <div className="text-xs uppercase font-semibold tracking-wider text-accent">Enterprise Comparison</div>
            <h2 className="text-3xl font-bold tracking-tight text-text-primary">
              Why Generic LLMs Fail in Enterprise Ops
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="rounded-2xl border border-border bg-surface-muted/40 p-8 space-y-4">
              <div className="font-bold text-base text-text-primary">
                Generic LLMs & Chatbots
              </div>
              <ul className="space-y-3 text-xs text-text-muted">
                <li className="flex items-start gap-2">
                  <span className="text-text-muted font-bold">✕</span>
                  <span><strong>Hallucinates facts:</strong> Generates plausible-sounding but fictitious procedure details when answers are unknown.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-text-muted font-bold">✕</span>
                  <span><strong>No audit trail:</strong> Cannot link answers to specific page numbers or authorized revision dates.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-text-muted font-bold">✕</span>
                  <span><strong>Data privacy risk:</strong> Corporate prompts and secrets may be reused for public AI training cycles.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-text-muted font-bold">✕</span>
                  <span><strong>No clearance tiers:</strong> Internal documents are exposed indiscriminately without role-based access checks.</span>
                </li>
              </ul>
            </div>

            <div className="rounded-2xl border border-border bg-surface p-8 space-y-4">
              <div className="font-bold text-base text-text-primary flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-success" /> KnowFlow AI Enterprise
              </div>
              <ul className="space-y-3 text-xs text-text-secondary">
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
                  <span><strong>DPDPA & GDPR Aligned Controls:</strong> Customer data is isolated in private PostgreSQL partitions and never shared for model training.</span>
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
          <h2 className="text-3xl font-extrabold text-text-primary">
            Ready to Empower Your Organization with Grounded SOPs?
          </h2>
          <p className="text-sm text-text-muted max-w-xl mx-auto">
            Stop guessing. Ensure every team member gets exact, verified answers from your source documents.
          </p>
          <div className="flex justify-center gap-4 pt-2">
            <Link
              href="/register"
              className="rounded-xl bg-accent px-8 py-3 text-sm font-semibold text-accent-foreground hover:bg-accent/90 transition-colors shadow-md"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-8 text-xs text-text-muted">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-accent" />
            <span>&copy; 2026 KnowFlow AI. Enterprise Knowledge & SOP Assistant.</span>
          </div>
          <div className="flex items-center space-x-6">
            <Link href="/security" className="hover:text-text-primary transition-colors flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-success" /> Security & Privacy Controls
            </Link>
            <Link href="/login" className="hover:text-text-primary transition-colors">Sign In</Link>
            <Link href="/register" className="hover:text-text-primary transition-colors">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
