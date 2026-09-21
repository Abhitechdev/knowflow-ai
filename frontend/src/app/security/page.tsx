"use client";

import Link from "next/link";
import {
  ShieldCheck,
  Lock,
  FileCheck2,
  Database,
  UserCheck,
  Server,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Scale,
  EyeOff,
  Cpu,
  ArrowRight,
} from "lucide-react";

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-background text-text-primary selection:bg-accent/20">
      {/* Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-surface-muted text-accent transition-transform group-hover:scale-105">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-text-primary">KnowFlow AI</span>
              <span className="hidden sm:inline-block ml-2 text-xs text-text-muted px-2 py-0.5 rounded-full border border-border bg-surface-muted">
                Trust & Compliance Center
              </span>
            </div>
          </Link>

          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="text-xs font-medium text-text-muted hover:text-text-primary transition-colors flex items-center gap-1"
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Back to Home
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-accent px-3.5 py-1.5 text-xs font-medium text-accent-foreground hover:bg-accent/90 transition-colors shadow-sm"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-surface-muted/50 to-background py-16 sm:py-24">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3.5 py-1 text-xs font-medium text-text-primary mb-6">
            <ShieldCheck className="h-4 w-4 text-accent" /> Security and Privacy Controls Architecture
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl text-text-primary">
            Security and Privacy Controls Implemented by KnowFlow AI
          </h1>
          <p className="mt-4 text-base sm:text-lg text-text-muted max-w-3xl mx-auto leading-relaxed">
            Detailed technical and organizational controls designed to protect enterprise Standard Operating Procedures, intellectual property, and personal data.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-4 text-xs text-text-secondary">
            <div className="flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> AES-256 Storage & TLS 1.3 Transit
            </div>
            <div className="flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> Zero AI Model Training Policy
            </div>
            <div className="flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> Row-Level Multi-Tenant Isolation
            </div>
            <div className="flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5">
              <CheckCircle2 className="h-4 w-4 text-success" /> Audit Logging & Access Telemetry
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 space-y-16">
        
        {/* Section 1: DPDP Act 2023 Alignment */}
        <section id="dpdpa" className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-text-primary">
                Digital Personal Data Protection Act, 2023 (DPDP Act)
              </h2>
              <p className="text-sm text-text-muted">
                How KnowFlow AI aligns with India&apos;s statutory personal data governance standards.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-semibold text-sm">
                <FileCheck2 className="h-4 w-4 text-accent" />
                <span>1. Purpose Limitation & Data Minimization</span>
              </div>
              <p className="text-xs text-text-muted leading-relaxed">
                KnowFlow AI processes documents solely for semantic indexing and search retrieval within your designated tenant workspace. Data is never repurposed, pooled, or indexed outside your authorized scope.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-semibold text-sm">
                <UserCheck className="h-4 w-4 text-accent" />
                <span>2. Data Principal Rights (Correction & Erasure)</span>
              </div>
              <p className="text-xs text-text-muted leading-relaxed">
                In compliance with Section 12 of the DPDP Act, workspace administrators have direct, programmatic control to immediately delete documents, conversation histories, and vector embeddings with complete hard deletion.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-semibold text-sm">
                <ShieldCheck className="h-4 w-4 text-accent" />
                <span>3. Reasonable Security Safeguards (Section 8(5))</span>
              </div>
              <p className="text-xs text-text-muted leading-relaxed">
                All data in transit is protected with TLS 1.3 encryption, and all persistent storage (PostgreSQL relational DB, pgvector embeddings, and object storage) is encrypted with AES-256 at rest.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-semibold text-sm">
                <Lock className="h-4 w-4 text-accent" />
                <span>4. Grievance Redressal & Access Control</span>
              </div>
              <p className="text-xs text-text-muted leading-relaxed">
                Every query, access request, and permission modification is immutably timestamped in audit logs with user identifiers and IP addresses to ensure full regulatory traceability.
              </p>
            </div>
          </div>
        </section>

        {/* Section 2: Zero AI Training Guarantee */}
        <section className="rounded-2xl border border-border bg-surface-muted/40 p-8 sm:p-10 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent uppercase tracking-wider">
                <EyeOff className="h-4 w-4" /> Confidentiality Assurance
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-text-primary">
                Zero AI Model Training on Enterprise Data
              </h3>
              <p className="text-xs sm:text-sm text-text-muted leading-relaxed">
                Your company SOPs, manuals, contracts, and chat queries are never used to train, retrain, or fine-tune public foundation models. We interface exclusively with enterprise zero-retention API endpoints.
              </p>
            </div>
            <div className="shrink-0 flex flex-col gap-2">
              <div className="rounded-lg border border-border bg-surface px-4 py-3 text-xs">
                <div className="font-semibold text-text-primary">In-Memory Prompt Evaluation</div>
                <div className="text-text-muted">Prompts discarded immediately after generation</div>
              </div>
              <div className="rounded-lg border border-border bg-surface px-4 py-3 text-xs">
                <div className="font-semibold text-text-primary">Isolated Vector Partitioning</div>
                <div className="text-text-muted">Tenant-scoped PostgreSQL HNSW index</div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Grounded Answering & Hallucination Prevention */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-text-primary">
                Grounded Answering & Hallucination Safeguards
              </h2>
              <p className="text-sm text-text-muted">
                How our deterministic retrieval pipeline eliminates unauthorized or fabricated responses.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="text-accent font-bold text-sm">1. Multi-Tier Semantic Chunking</div>
              <p className="text-xs text-text-muted leading-relaxed">
                Documents are split preserving page numbers, section headers, and semantic boundaries rather than arbitrary token cuts.
              </p>
            </div>
            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="text-accent font-bold text-sm">2. Hybrid Dense + Sparse Retrieval</div>
              <p className="text-xs text-text-muted leading-relaxed">
                Combines high-dimensional OpenAI vector embeddings with BM25 keyword matching to ensure exact technical term recall.
              </p>
            </div>
            <div className="rounded-xl border border-border bg-surface p-6 space-y-3">
              <div className="text-accent font-bold text-sm">3. Grounding Refusal Policy</div>
              <p className="text-xs text-text-muted leading-relaxed">
                If documents do not contain direct evidence for a query, the model explicitly refuses under policy rather than hallucinating assumptions.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: Role-Based Access Control (RBAC) */}
        <section className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
              <UserCheck className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-text-primary">
                Role-Based Access Control & Clearance Tiers
              </h2>
              <p className="text-sm text-text-muted">
                Fine-grained permission boundaries prevent unauthorized internal document exposure.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-border bg-surface">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border bg-surface-muted/50 text-text-primary">
                <tr>
                  <th className="p-3.5 font-semibold">User Role</th>
                  <th className="p-3.5 font-semibold">Authorized Document Clearance</th>
                  <th className="p-3.5 font-semibold">Administrative Rights</th>
                  <th className="p-3.5 font-semibold">Audit Visibility</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border text-text-secondary">
                <tr>
                  <td className="p-3.5 font-semibold text-text-primary">ADMIN</td>
                  <td className="p-3.5">Public, Internal, Confidential, Restricted</td>
                  <td className="p-3.5 text-success">Full System & Member Management</td>
                  <td className="p-3.5">Full Workspace Audit Logs</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-semibold text-text-primary">MANAGER</td>
                  <td className="p-3.5">Public, Internal, Confidential, Departmental</td>
                  <td className="p-3.5">Document Ingestion & Team Access</td>
                  <td className="p-3.5">Department Logs</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-semibold text-text-primary">COMPLIANCE OFFICER</td>
                  <td className="p-3.5">All Internal SOPs & Compliance Filings</td>
                  <td className="p-3.5">Read & Audit Inspection</td>
                  <td className="p-3.5">Full Compliance Telemetry</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-semibold text-text-primary">EMPLOYEE / OPERATOR</td>
                  <td className="p-3.5">Public, Internal, Departmental Only</td>
                  <td className="p-3.5 text-text-muted">Query & Search Only</td>
                  <td className="p-3.5 text-text-muted">Personal Query History</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* CTA Card */}
        <section className="rounded-2xl border border-border bg-gradient-to-br from-surface-muted via-surface to-surface-muted p-8 sm:p-12 text-center space-y-6">
          <h3 className="text-2xl font-bold text-text-primary">
            Deploy KnowFlow AI in Your Enterprise Today
          </h3>
          <p className="text-sm text-text-muted max-w-xl mx-auto">
            Experience reliable, grounded AI knowledge retrieval with complete compliance and data privacy guarantees.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-accent-foreground hover:bg-accent/90 transition-colors shadow-md"
            >
              Create Free Workspace <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-lg border border-border bg-surface px-6 py-2.5 text-sm font-medium text-text-primary hover:bg-surface-hover transition-colors"
            >
              Sign In to Existing Account
            </Link>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-8 text-xs text-text-muted">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-accent" />
            <span>&copy; 2026 KnowFlow AI. All rights reserved.</span>
          </div>
          <div className="flex items-center space-x-6">
            <Link href="/" className="hover:text-text-primary transition-colors">Home</Link>
            <Link href="/security" className="text-text-primary font-medium">Security & DPDP</Link>
            <Link href="/login" className="hover:text-text-primary transition-colors">Sign In</Link>
            <Link href="/register" className="hover:text-text-primary transition-colors">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
