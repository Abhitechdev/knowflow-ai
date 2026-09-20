"use client";

import { useState, useEffect, useCallback } from "react";
import {
  FileText,
  Upload,
  RefreshCw,
  Search,
  Clock,
  AlertTriangle,
  Download,
  Trash2,
  Eye,
  X,
  Layers,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import {
  fetchDocuments,
  fetchDocumentDetail,
  uploadDocument,
  deleteDocument,
  DocumentItem,
  DocumentDetail,
} from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadAccessLevel, setUploadAccessLevel] = useState("WORKSPACE");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Inspect modal state
  const [inspectDocId, setInspectDocId] = useState<string | null>(null);
  const [inspectDetail, setInspectDetail] = useState<DocumentDetail | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);

  // Delete state
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    const res = await fetchDocuments({ search: searchQuery, status: statusFilter });
    if (res.error) {
      setErrorMessage(res.error);
    } else if (res.data) {
      setDocuments(res.data.items);
      setErrorMessage(null);
    }
    setLoading(false);
    setRefreshing(false);
  }, [searchQuery, statusFilter]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // Auto-poll if any document is PROCESSING
  useEffect(() => {
    const hasProcessing = documents.some((d) => d.status === "PROCESSING" || d.status === "UPLOADED");
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      loadDocuments();
    }, 3000);
    return () => clearInterval(interval);
  }, [documents, loadDocuments]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadDocuments();
  };

  const handleOpenInspect = async (id: string) => {
    setInspectDocId(id);
    setInspectLoading(true);
    const res = await fetchDocumentDetail(id);
    if (res.data) {
      setInspectDetail(res.data);
    }
    setInspectLoading(false);
  };

  const handleCloseInspect = () => {
    setInspectDocId(null);
    setInspectDetail(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadFile(file);
      if (!uploadTitle) {
        setUploadTitle(file.name.replace(/\.[^/.]+$/, ""));
      }
      setUploadError(null);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError("Please select a valid document file.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", uploadFile);
    if (uploadTitle.trim()) {
      formData.append("title", uploadTitle.trim());
    }
    formData.append("access_level", uploadAccessLevel);

    const res = await uploadDocument(formData);
    if (res.error) {
      setUploadError(res.error);
      setIsUploading(false);
    } else {
      setIsUploading(false);
      setIsUploadOpen(false);
      setUploadFile(null);
      setUploadTitle("");
      loadDocuments();
    }
  };

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"? This will remove its vectors and storage files.`)) {
      return;
    }
    setDeletingId(id);
    const res = await deleteDocument(id);
    if (res.success) {
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (inspectDocId === id) handleCloseInspect();
    } else {
      alert(res.error || "Failed to delete document");
    }
    setDeletingId(null);
  };

  const formatFileSize = (bytes: number) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getFormatBadge = (type: string) => {
    const t = type.toLowerCase();
    switch (t) {
      case "pdf":
        return { label: "PDF", bg: "bg-rose-500/10 text-rose-400 border-rose-500/20" };
      case "docx":
      case "doc":
        return { label: "DOCX", bg: "bg-blue-500/10 text-blue-400 border-blue-500/20" };
      case "txt":
        return { label: "TXT", bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
      case "md":
        return { label: "MD", bg: "bg-purple-500/10 text-purple-400 border-purple-500/20" };
      case "csv":
        return { label: "CSV", bg: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
      default:
        return { label: t.toUpperCase(), bg: "bg-zinc-800 text-zinc-300 border-zinc-700" };
    }
  };

  const totalChunksCount = documents.reduce((acc, d) => acc + (d.total_chunks || 0), 0);
  const readyDocsCount = documents.filter((d) => d.status === "READY").length;

  return (
    <div className="max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-semibold tracking-tight text-white">Document Pipeline</h1>
            <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-medium text-emerald-400">
              Phase 2 Active
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Enterprise SOPs and manuals ingested into Supabase Storage and pgvector.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="inline-flex items-center space-x-1.5 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            title="Refresh list"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-emerald-400" : ""}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setIsUploadOpen(true)}
            className="inline-flex items-center space-x-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-3.5 py-2 text-xs font-medium text-black transition-colors shadow-sm shadow-emerald-950"
          >
            <Upload className="h-3.5 w-3.5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Total Documents</span>
            <FileText className="h-3.5 w-3.5 text-zinc-500" />
          </div>
          <p className="text-lg font-semibold text-white">{documents.length}</p>
        </div>
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Indexed Chunks</span>
            <Layers className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <p className="text-lg font-semibold text-emerald-400">{totalChunksCount}</p>
        </div>
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Vector Status</span>
            <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <p className="text-lg font-semibold text-white">
            {readyDocsCount} <span className="text-xs text-zinc-500 font-normal">/ {documents.length} ready</span>
          </p>
        </div>
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3.5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Embedding Dim</span>
            <ShieldCheck className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <p className="text-lg font-semibold text-purple-300">384 <span className="text-xs text-zinc-500 font-normal">pgvector</span></p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-zinc-900/20 p-2 rounded-xl border border-zinc-800/60">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search documents by title or filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-zinc-800 bg-zinc-900/90 pl-9 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
        </div>

        <div className="flex items-center space-x-1">
          {["ALL", "READY", "PROCESSING", "FAILED"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-medium transition-colors ${
                statusFilter === status
                  ? "bg-zinc-800 text-white border border-zinc-700"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="rounded-xl border border-rose-500/20 bg-rose-950/20 p-3 text-xs text-rose-400 flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Documents Table */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/60 overflow-hidden shadow-sm">
        <div className="grid grid-cols-12 border-b border-zinc-800 bg-zinc-900/40 px-4 py-3 text-[11px] font-medium text-zinc-400 uppercase tracking-wider">
          <div className="col-span-5 sm:col-span-4">Document Title</div>
          <div className="col-span-2 sm:col-span-1">Type</div>
          <div className="hidden sm:block sm:col-span-2">Size</div>
          <div className="col-span-3 sm:col-span-2">Status</div>
          <div className="hidden sm:block sm:col-span-1">Chunks</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-zinc-500">
            <RefreshCw className="h-5 w-5 animate-spin mx-auto text-emerald-400 mb-2" />
            Loading documents from database...
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-zinc-800 bg-zinc-900 text-zinc-500">
              <FileText className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-zinc-200">No Documents Found</h3>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                {searchQuery
                  ? "No documents matched your search criteria."
                  : "Upload your company's SOPs, policies, and manuals to populate the knowledge base."}
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-zinc-800/60">
            {documents.map((doc) => {
              const badge = getFormatBadge(doc.file_type);
              return (
                <div
                  key={doc.id}
                  className="grid grid-cols-12 items-center px-4 py-3 text-xs hover:bg-zinc-900/40 transition-colors"
                >
                  {/* Title & filename */}
                  <div className="col-span-5 sm:col-span-4 min-w-0 pr-2">
                    <button
                      onClick={() => handleOpenInspect(doc.id)}
                      className="text-left font-medium text-zinc-200 hover:text-emerald-400 transition-colors truncate block max-w-full"
                    >
                      {doc.title}
                    </button>
                    <span className="text-[10px] text-zinc-500 truncate block">{doc.original_filename}</span>
                  </div>

                  {/* Format */}
                  <div className="col-span-2 sm:col-span-1">
                    <span
                      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-medium border ${badge.bg}`}
                    >
                      {badge.label}
                    </span>
                  </div>

                  {/* Size */}
                  <div className="hidden sm:block sm:col-span-2 text-zinc-400 text-[11px]">
                    {formatFileSize(doc.file_size_bytes)}
                  </div>

                  {/* Status */}
                  <div className="col-span-3 sm:col-span-2">
                    {doc.status === "READY" && (
                      <span className="inline-flex items-center space-x-1.5 text-emerald-400 text-[11px] font-medium">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        <span>Ready</span>
                      </span>
                    )}
                    {doc.status === "PROCESSING" && (
                      <span className="inline-flex items-center space-x-1.5 text-blue-400 text-[11px] font-medium">
                        <RefreshCw className="h-3 w-3 animate-spin" />
                        <span>Processing</span>
                      </span>
                    )}
                    {doc.status === "UPLOADED" && (
                      <span className="inline-flex items-center space-x-1.5 text-amber-400 text-[11px] font-medium">
                        <Clock className="h-3 w-3" />
                        <span>Queued</span>
                      </span>
                    )}
                    {doc.status === "FAILED" && (
                      <span
                        className="inline-flex items-center space-x-1 text-rose-400 text-[11px] font-medium cursor-help"
                        title={doc.error_message || "Ingestion failed"}
                      >
                        <AlertTriangle className="h-3 w-3" />
                        <span>Failed</span>
                      </span>
                    )}
                  </div>

                  {/* Chunks */}
                  <div className="hidden sm:block sm:col-span-1 text-zinc-400 text-[11px]">
                    {doc.total_chunks} <span className="text-[10px] text-zinc-500">chunks</span>
                  </div>

                  {/* Actions */}
                  <div className="col-span-2 flex items-center justify-end space-x-1.5">
                    <button
                      onClick={() => handleOpenInspect(doc.id)}
                      className="p-1 text-zinc-400 hover:text-white rounded hover:bg-zinc-800 transition-colors"
                      title="Inspect extracted chunks"
                    >
                      <Eye className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id, doc.title)}
                      disabled={deletingId === doc.id}
                      className="p-1 text-zinc-500 hover:text-rose-400 rounded hover:bg-zinc-800 transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Upload New Document</h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Supported formats: PDF, DOCX, TXT, MD, CSV (Max: 25 MB).
                </p>
              </div>
              <button
                onClick={() => setIsUploadOpen(false)}
                className="text-zinc-500 hover:text-white transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              {/* File Dropzone */}
              <div className="relative border-2 border-dashed border-zinc-800 hover:border-emerald-500/50 rounded-xl p-6 text-center transition-colors">
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.md,.csv"
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                />
                <div className="space-y-2">
                  <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400">
                    <Upload className="h-5 w-5" />
                  </div>
                  {uploadFile ? (
                    <div>
                      <p className="text-xs font-semibold text-emerald-400">{uploadFile.name}</p>
                      <p className="text-[10px] text-zinc-500">{formatFileSize(uploadFile.size)}</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-xs text-zinc-300 font-medium">Click or drag & drop to choose file</p>
                      <p className="text-[10px] text-zinc-500 mt-0.5">PDF, DOCX, TXT, MD, CSV</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Title input */}
              <div className="space-y-1">
                <label className="text-[11px] font-medium text-zinc-300">Document Title</label>
                <input
                  type="text"
                  placeholder="e.g. SOP-QA-042: Deviation Management"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:outline-none"
                />
              </div>

              {/* Access Level */}
              <div className="space-y-1">
                <label className="text-[11px] font-medium text-zinc-300">Access Level</label>
                <select
                  value={uploadAccessLevel}
                  onChange={(e) => setUploadAccessLevel(e.target.value)}
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-white focus:border-emerald-500/50 focus:outline-none"
                >
                  <option value="WORKSPACE">WORKSPACE — All Employees</option>
                  <option value="DEPARTMENT">DEPARTMENT — Specific Team</option>
                  <option value="PRIVATE">PRIVATE — Uploader Only</option>
                  <option value="ADMIN_ONLY">ADMIN_ONLY — Compliance Admins</option>
                </select>
              </div>

              {uploadError && (
                <div className="rounded-lg border border-rose-500/20 bg-rose-950/20 p-2.5 text-xs text-rose-400">
                  {uploadError}
                </div>
              )}

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="rounded-lg border border-zinc-800 px-3 py-2 text-xs font-medium text-zinc-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading || !uploadFile}
                  className="inline-flex items-center space-x-2 rounded-lg bg-emerald-500 px-4 py-2 text-xs font-medium text-black hover:bg-emerald-400 transition-colors disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      <span>Ingesting Document...</span>
                    </>
                  ) : (
                    <span>Upload & Ingest</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Inspect Chunks Modal */}
      {inspectDocId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-3xl max-h-[85vh] flex flex-col rounded-2xl border border-zinc-800 bg-zinc-950 shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-zinc-800 p-4">
              <div className="min-w-0 pr-4">
                <h3 className="text-sm font-semibold text-white truncate">
                  {inspectDetail?.title || "Document Details"}
                </h3>
                <p className="text-[11px] text-zinc-400 mt-0.5">
                  Extracted Pages: {inspectDetail?.page_count || 0} | Total Chunks:{" "}
                  {inspectDetail?.chunks.length || 0} | Dimension: 384
                </p>
              </div>
              <div className="flex items-center space-x-2 shrink-0">
                {inspectDetail?.signed_url && (
                  <a
                    href={inspectDetail.signed_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1.5 text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
                  >
                    <Download className="h-3 w-3" />
                    <span>Download File</span>
                  </a>
                )}
                <button
                  onClick={handleCloseInspect}
                  className="text-zinc-500 hover:text-white transition-colors p-1"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {inspectLoading ? (
                <div className="p-12 text-center text-xs text-zinc-500">
                  <RefreshCw className="h-5 w-5 animate-spin mx-auto text-emerald-400 mb-2" />
                  Loading chunk data from Supabase...
                </div>
              ) : inspectDetail?.chunks.length === 0 ? (
                <p className="text-xs text-zinc-500 text-center py-8">
                  No chunks have been generated yet for this document.
                </p>
              ) : (
                inspectDetail?.chunks.map((chunk) => (
                  <div
                    key={chunk.id}
                    className="rounded-xl border border-zinc-800/80 bg-zinc-900/30 p-3.5 space-y-2 hover:border-zinc-700 transition-colors"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-emerald-400">
                        Chunk #{chunk.chunk_index + 1}
                      </span>
                      <div className="flex items-center space-x-3 text-zinc-400 text-[10px]">
                        <span>Page {chunk.page_number}</span>
                        <span>•</span>
                        <span className="text-zinc-300 font-medium truncate max-w-xs">
                          {chunk.section_heading}
                        </span>
                      </div>
                    </div>
                    <p className="text-xs leading-relaxed text-zinc-300 whitespace-pre-wrap font-sans bg-black/20 p-2.5 rounded-lg border border-zinc-800/40">
                      {chunk.content}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
