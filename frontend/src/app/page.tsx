"use client";

import Link from "next/link";
import { SystemHealthBadge } from "@/components/system-health-badge";
import {
  Check,
  FileText,
  Bot,
  Layers,
  Lock,
  ArrowUpRight,
  MessageSquare,
  BookOpen,
} from "lucide-react";

export default function DashboardPage() {
  const verifiedItems = [
    {
      title: "Repository & Monorepo Layout",
      detail: "Clean separation between backend (FastAPI), frontend (Next.js 14), and documentation.",
      status: "Verified",
    },
    {
      title: "FastAPI Backend & Async Core",
      detail: "Starts natively on Windows without requiring Docker. Serves /api/health and /api/v1/health.",
      status: "Verified",
    },
    {
      title: "Full PRD Database Schema",
      detail: "16 domain models created (Workspaces, Users, Documents, Chunks, Chat, Feedback, Evals, Audit).",
      status: "Verified",
    },
    {
      title: "Database Connection Abstraction",
      detail: "Targeting PostgreSQL + pgvector with graceful unconfigured state handling for local dev.",
      status: "Verified",
    },
    {
      title: "Authentication Abstraction Layer",
      detail: "Abstract AuthProvider interface implemented for Supabase Auth without vendor lock-in.",
      status: "Verified",
    },
    {
      title: "Automated Test Suite",
      detail: "8/8 backend unit & integration tests passing (pytest). Zero mock shortcuts.",
      status: "Verified",
    },
  ];

  const upcomingPhases = [
    {
      phase: "Phase 2 (Active)",
      title: "Document Ingestion Pipeline",
      icon: FileText,
      href: "/documents",
      description:
        "Supabase Storage connection, document extraction (PDF, DOCX, TXT), page metadata, chunking, embeddings, and pgvector persistence.",
    },
    {
      phase: "Phase 3 (Live)",
      title: "RAG & Grounded Citations",
      icon: Bot,
      href: "/chat",
      description:
        "Hybrid retrieval (dense vector + sparse BM25), reciprocal rank fusion, evidence sufficiency check, grounded answering policy with verified citations.",
    },
    {
      phase: "Phase 4 - 9",
      title: "Enterprise Hardening & Admin",
      icon: Lock,
      href: "/settings",
      description:
        "Workspace isolation, RBAC, document permissions, audit logs, automated evaluation dataset, and production deployment.",
    },
  ];

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Welcome Banner */}
      <div className="rounded-2xl border border-zinc-800 bg-gradient-to-b from-zinc-900/60 to-zinc-950/80 p-6 sm:p-8 backdrop-blur-xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-300">
              <Layers className="h-3.5 w-3.5" />
              <span>KnowFlow AI • Phase 1 Foundation</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-white">
              Turn company documents into reliable, searchable knowledge.
            </h1>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Enterprise SOP and knowledge assistant built with strict grounding, authoritative page-level
              citations, tenant data isolation, and comprehensive quality evaluation.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5 shrink-0">
            <Link
              href="/chat"
              className="inline-flex items-center space-x-2 rounded-lg border border-zinc-700 bg-zinc-800/90 px-3.5 py-2 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition-colors shadow-sm"
            >
              <MessageSquare className="h-3.5 w-3.5" />
              <span>Ask AI (Preview)</span>
            </Link>
            <Link
              href="/documents"
              className="inline-flex items-center space-x-2 rounded-lg border border-zinc-700 bg-zinc-800/90 px-3.5 py-2 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition-colors shadow-sm"
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Documents (Preview)</span>
            </Link>
          </div>
        </div>

        {/* Live Connectivity Probe Component */}
        <div className="border-t border-zinc-800/80 pt-6">
          <SystemHealthBadge />
        </div>
      </div>

      {/* Suggested Questions Preview (PRD #9 requirement) */}
      <div className="rounded-xl border border-zinc-800/80 bg-zinc-950/40 p-6 space-y-4">
        <div className="flex items-center space-x-2.5">
          <BookOpen className="h-4 w-4 text-indigo-400" />
          <h2 className="text-sm font-semibold text-zinc-100">Sample SOP Inquiries (Available in Phase 3)</h2>
        </div>
        <p className="text-xs text-zinc-400">
          Once synthetic demo SOPs and company manuals are ingested in Phase 2, users will be able to query:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/30 p-3 text-xs text-zinc-300">
            &ldquo;What is the procedure for handling a deviation?&rdquo;
          </div>
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/30 p-3 text-xs text-zinc-300">
            &ldquo;What is the incident escalation process?&rdquo;
          </div>
          <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/30 p-3 text-xs text-zinc-300">
            &ldquo;What are the requirements for leave approval?&rdquo;
          </div>
        </div>
      </div>

      {/* Phase 1 Verification Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-zinc-100">Phase 1 Acceptance Criteria Verification</h2>
            <p className="text-xs text-zinc-400">All architectural components verified before beginning ingestion</p>
          </div>
          <span className="rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1 text-xs font-medium text-emerald-400">
            6 of 6 Core Modules Ready
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {verifiedItems.map((item) => (
            <div
              key={item.title}
              className="rounded-xl border border-zinc-800/80 bg-zinc-900/30 p-4 space-y-2 hover:border-zinc-700/80 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
                  <Check className="h-3.5 w-3.5" />
                </div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400/90 font-medium">
                  {item.status}
                </span>
              </div>
              <h3 className="text-xs font-medium text-zinc-200">{item.title}</h3>
              <p className="text-[11px] leading-relaxed text-zinc-400">{item.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Milestones */}
      <div className="space-y-4">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">Upcoming Implementation Roadmap</h2>
          <p className="text-xs text-zinc-400">
            Per master PRD, phases proceed sequentially upon explicit verification and approval.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {upcomingPhases.map((phase) => {
            const Icon = phase.icon;
            return (
              <Link
                key={phase.phase}
                href={phase.href}
                className="group rounded-xl border border-zinc-800 bg-zinc-950/60 p-5 space-y-2 hover:border-zinc-700 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-zinc-300">
                    <Icon className="h-4 w-4 text-indigo-400" />
                    <span className="text-xs font-semibold">{phase.phase}</span>
                  </div>
                  <ArrowUpRight className="h-3.5 w-3.5 text-zinc-500 group-hover:text-zinc-200 transition-colors" />
                </div>
                <h3 className="text-xs font-medium text-zinc-200">{phase.title}</h3>
                <p className="text-xs leading-relaxed text-zinc-500">{phase.description}</p>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
