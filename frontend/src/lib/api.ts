export interface HealthData {
  status: "healthy" | "degraded" | "error";
  version: string;
  environment: string;
  database: {
    status: string;
    connected: boolean;
    message?: string;
  };
  auth: {
    provider: string;
    configured: boolean;
    message?: string;
  };
  timestamp: string;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  department_id: string | null;
  uploaded_by_user_id: string | null;
  title: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  storage_path: string;
  status: "UPLOADED" | "PROCESSING" | "READY" | "FAILED";
  error_message: string | null;
  access_level: string;
  page_count: number;
  total_chunks: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  page_number: number;
  section_heading: string;
  content: string;
  created_at: string;
}

export interface DocumentDetail extends DocumentItem {
  chunks: DocumentChunk[];
  signed_url: string | null;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  size: number;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function fetchSystemHealth(): Promise<{
  data: HealthData | null;
  error: string | null;
  latencyMs: number;
}> {
  const start = performance.now();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const res = await fetch(`${BACKEND_URL}/api/health`, {
      signal: controller.signal,
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });
    clearTimeout(timeoutId);

    const latencyMs = Math.round(performance.now() - start);

    if (!res.ok) {
      return {
        data: null,
        error: `Server responded with status ${res.status}`,
        latencyMs,
      };
    }

    const data: HealthData = await res.json();
    return { data, error: null, latencyMs };
  } catch (err: unknown) {
    const latencyMs = Math.round(performance.now() - start);
    const message = err instanceof Error ? err.message : "Failed to connect to backend service";
    return { data: null, error: message, latencyMs };
  }
}

export async function fetchDocuments(params?: {
  search?: string;
  status?: string;
}): Promise<{ data: DocumentListResponse | null; error: string | null }> {
  try {
    const url = new URL(`${BACKEND_URL}/api/documents`);
    if (params?.search) url.searchParams.set("search", params.search);
    if (params?.status && params.status !== "ALL") url.searchParams.set("status", params.status);

    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) {
      return { data: null, error: `Failed to fetch documents: HTTP ${res.status}` };
    }
    const data: DocumentListResponse = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Network error fetching documents",
    };
  }
}

export async function fetchDocumentDetail(
  id: string
): Promise<{ data: DocumentDetail | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/documents/${id}`, { cache: "no-store" });
    if (!res.ok) {
      return { data: null, error: `Failed to fetch document: HTTP ${res.status}` };
    }
    const data: DocumentDetail = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Network error fetching document detail",
    };
  }
}

export async function uploadDocument(
  formData: FormData
): Promise<{ data: { document: DocumentItem; message: string } | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      return { data: null, error: errorData.detail || "Upload failed" };
    }
    const data = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Network error during document upload",
    };
  }
}

export async function deleteDocument(id: string): Promise<{ success: boolean; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/documents/${id}`, {
      method: "DELETE",
    });
    if (!res.ok && res.status !== 204) {
      return { success: false, error: `Failed to delete document: HTTP ${res.status}` };
    }
    return { success: true, error: null };
  } catch (err: unknown) {
    return {
      success: false,
      error: err instanceof Error ? err.message : "Network error deleting document",
    };
  }
}

// -----------------------------------------------------------------------------
// Phase 3: RAG Chat, Search & Feedback Interfaces
// -----------------------------------------------------------------------------

export interface CitationItem {
  id?: string;
  document_id: string;
  chunk_id?: string | null;
  document_title: string;
  page_number: number;
  section_heading: string;
  relevant_text: string;
  confidence: number;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_type: "USER" | "ASSISTANT" | "SYSTEM";
  content: string;
  created_at: string;
  sources?: CitationItem[];
}

export interface ConversationSummary {
  id: string;
  workspace_id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

export interface ChatQueryResponse {
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  query: string;
  answer: string;
  is_grounded: boolean;
  policy_applied: string;
  citations: CitationItem[];
  latency_ms: number;
  tokens_used: number;
  model_used: string;
  grounding_status: "SUFFICIENT" | "REFUSED_INSUFFICIENT_EVIDENCE";
}

export async function sendChatQuery(params: {
  message: string;
  conversation_id?: string | null;
  department_filter?: string | null;
}): Promise<{ data: ChatQueryResponse | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/chat/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      return { data: null, error: err.detail || "Query failed" };
    }
    const data: ChatQueryResponse = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Network error during AI query" };
  }
}

export async function fetchConversations(): Promise<{
  data: ConversationSummary[] | null;
  error: string | null;
}> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/chat/conversations`, { cache: "no-store" });
    if (!res.ok) return { data: null, error: `Failed to fetch conversations: HTTP ${res.status}` };
    const data: ConversationSummary[] = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Network error" };
  }
}

export async function fetchConversationDetail(
  id: string
): Promise<{ data: ConversationDetail | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/chat/conversations/${id}`, { cache: "no-store" });
    if (!res.ok) return { data: null, error: `Failed to fetch conversation: HTTP ${res.status}` };
    const data: ConversationDetail = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Network error" };
  }
}

export async function deleteConversation(id: string): Promise<{ success: boolean; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/chat/conversations/${id}`, { method: "DELETE" });
    if (!res.ok && res.status !== 204) {
      return { success: false, error: `HTTP ${res.status}` };
    }
    return { success: true, error: null };
  } catch (err: unknown) {
    return { success: false, error: err instanceof Error ? err.message : "Network error" };
  }
}

export async function submitFeedback(params: {
  message_id: string;
  rating: number;
  comments?: string;
  category?: string;
}): Promise<{ success: boolean; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/chat/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return { success: res.ok, error: res.ok ? null : `HTTP ${res.status}` };
  } catch (err: unknown) {
    return { success: false, error: err instanceof Error ? err.message : "Feedback submission error" };
  }
}

export interface SearchChunkResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  file_type: string;
  page_number: number;
  section_heading: string;
  snippet: string;
  dense_score: number;
  sparse_score: number;
  rrf_score: number;
  relevance_pct: number;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchChunkResult[];
  latency_ms: number;
}

export async function performHybridSearch(params: {
  query: string;
  department_id?: string | null;
  top_k?: number;
}): Promise<{ data: SearchResponse | null; error: string | null }> {
  try {
    const url = new URL(`${BACKEND_URL}/api/v1/search`);
    url.searchParams.set("query", params.query);
    if (params.department_id) url.searchParams.set("department_id", params.department_id);
    if (params.top_k) url.searchParams.set("top_k", params.top_k.toString());

    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) return { data: null, error: `Search failed: HTTP ${res.status}` };
    const data: SearchResponse = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Network error during search" };
  }
}

export interface AdminStats {
  total_documents: number;
  total_chunks: number;
  total_conversations: number;
  total_messages: number;
  total_audit_events: number;
  positive_feedback_count: number;
  negative_feedback_count: number;
  grounded_answering_policy: string;
  hybrid_reranker_status: string;
}

export interface AuditLogRecord {
  id: string;
  workspace_id: string;
  user_id: string | null;
  action: string;
  ip_address: string | null;
  metadata_json: string;
  created_at: string;
}

export interface CaseEvaluationResult {
  case_id: string;
  question: string;
  category: string;
  is_out_of_scope: boolean;
  retrieved_doc_titles: string[];
  retrieved_sections: string[];
  hit_at_1: number;
  hit_at_3: number;
  hit_at_5: number;
  mrr: number;
  ndcg_at_5: number;
  is_grounded: boolean;
  grounding_status: string;
  faithfulness_score: number;
  is_faithful: boolean;
  is_false_positive: boolean;
  is_false_negative: boolean;
  latency_ms: number;
  passed: boolean;
}

export interface EvaluationSummary {
  total_cases: number;
  in_scope_cases: number;
  out_of_scope_cases: number;
  passed_cases: number;
  failed_cases: number;
  pass_rate_pct: number;
  hit_rate_at_1: number;
  hit_rate_at_3: number;
  hit_rate_at_5: number;
  mrr: number;
  ndcg_at_5: number;
  avg_faithfulness: number;
  false_positives: number;
  false_negatives: number;
  refusal_accuracy_pct: number;
  avg_latency_ms: number;
  case_results: CaseEvaluationResult[];
}

export async function fetchAdminStats(): Promise<{ data: AdminStats | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/admin/stats`, { cache: "no-store" });
    if (!res.ok) return { data: null, error: `HTTP ${res.status}` };
    const data: AdminStats = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Failed to fetch stats" };
  }
}

export async function fetchAuditLogs(action?: string): Promise<{ data: AuditLogRecord[] | null; error: string | null }> {
  try {
    const url = new URL(`${BACKEND_URL}/api/v1/admin/audit-logs`);
    if (action) url.searchParams.set("action", action);
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) return { data: null, error: `HTTP ${res.status}` };
    const data: AuditLogRecord[] = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Failed to fetch audit logs" };
  }
}

export async function triggerEvaluationBenchmark(): Promise<{ data: EvaluationSummary | null; error: string | null }> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/evaluation/run`, {
      method: "POST",
      cache: "no-store",
    });
    if (!res.ok) return { data: null, error: `Evaluation failed: HTTP ${res.status}` };
    const data: EvaluationSummary = await res.json();
    return { data, error: null };
  } catch (err: unknown) {
    return { data: null, error: err instanceof Error ? err.message : "Evaluation network error" };
  }
}



