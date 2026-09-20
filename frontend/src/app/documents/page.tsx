"use client";

import { useEffect, useState } from "react";
import { fetchDocuments, uploadDocument, deleteDocument, DocumentItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  FileText,
  Upload,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  RefreshCw,
} from "lucide-react";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Only admins can delete, we will assume true for now or skip if authorized logic is complex. 
  // For a real app, we would check the user role from Supabase or context.

  const loadDocuments = async () => {
    try {
      setError(null);
      const res = await fetchDocuments();
      setDocuments(res.items);
    } catch (err: any) {
      setError(err.message || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    // Poll every 10 seconds to update statuses
    const interval = setInterval(() => {
      loadDocuments();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(formData);
      await loadDocuments();
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
      // Reset input
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await deleteDocument(id);
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (err: any) {
      setError(err.message || "Failed to delete document");
    }
  };

    const getStatusIcon = (status: string) => {
      switch (status) {
        case "READY":
          return <CheckCircle2 className="h-4 w-4 text-success" />;
        case "PROCESSING":
          return <Loader2 className="h-4 w-4 text-warning animate-spin" />;
        case "UPLOADED":
          return <Clock className="h-4 w-4 text-text-muted" />;
        case "FAILED":
          return <AlertCircle className="h-4 w-4 text-danger" />;
        default:
          return <FileText className="h-4 w-4 text-text-muted" />;
      }
    };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Documents</h1>
          <p className="text-sm text-text-muted mt-1">Manage standard operating procedures and knowledge base files.</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button 
            onClick={loadDocuments} 
            variant="outline"
            size="icon"
            title="Refresh"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading && documents.length === 0 ? "animate-spin" : ""}`} />
          </Button>
          
          <Button asChild>
            <label className="cursor-pointer relative flex items-center justify-center">
              {!uploading && <Upload className="mr-2 h-4 w-4" />}
              {uploading && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
              <span>{uploading ? "Uploading..." : "Upload File"}</span>
              <input
                type="file"
                className="sr-only"
                disabled={uploading}
                accept=".pdf,.docx,.txt,.md,.csv"
                onChange={handleFileUpload}
              />
            </label>
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-danger/20 bg-danger/10 p-4 flex items-center space-x-3 text-danger">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <div className="rounded-xl border border-border bg-surface overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-surface-muted">
              <tr>
                <th scope="col" className="px-6 py-4 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Title
                </th>
                <th scope="col" className="px-6 py-4 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-4 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-4 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Size
                </th>
                <th scope="col" className="px-6 py-4 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading && documents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <Loader2 className="h-6 w-6 animate-spin text-text-muted mx-auto" />
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-sm text-text-muted">
                    <div className="flex flex-col items-center justify-center space-y-3">
                      <div className="h-12 w-12 rounded-full bg-surface-muted flex items-center justify-center border border-border">
                        <FileText className="h-6 w-6 text-text-muted" />
                      </div>
                      <p>No documents found.</p>
                      <p className="text-xs text-text-muted">Upload a file to get started.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-surface-hover transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-text-muted shrink-0" />
                        <div>
                          <div className="text-sm font-medium text-text-primary">{doc.title}</div>
                          <div className="text-xs text-text-muted mt-0.5 font-mono">{doc.id.substring(0,8)}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center rounded-md border border-border bg-surface-muted px-2 py-1 text-xs font-medium text-text-muted uppercase">
                        {doc.file_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(doc.status)}
                        <span className={`text-xs font-medium ${
                          doc.status === "READY" ? "text-success" :
                          doc.status === "PROCESSING" ? "text-warning" :
                          doc.status === "FAILED" ? "text-danger" :
                          "text-text-muted"
                        }`}>
                          {doc.status}
                        </span>
                      </div>
                      {doc.error_message && (
                        <div className="text-[10px] text-danger mt-1 max-w-[200px] truncate" title={doc.error_message}>
                          {doc.error_message}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-muted font-mono">
                      {(doc.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Button
                        onClick={() => handleDelete(doc.id)}
                        variant="ghost"
                        size="icon"
                        className="text-text-muted hover:text-danger hover:bg-danger/10"
                        title="Delete document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
