import { createClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const ENV = process.env.NEXT_PUBLIC_ENV || "development";

if (!API_URL && ENV !== "development") {
  throw new Error("NEXT_PUBLIC_API_URL is required in staging and production environments.");
}

const BACKEND_URL = (API_URL || (ENV === "development" ? "http://localhost:8000" : "")).replace(/\/$/, "");

type FetchMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface FetchOptions extends RequestInit {
  method?: FetchMethod;
  timeoutMs?: number;
  skipAuth?: boolean;
}

export function getSafeErrorMessage(status: number, rawMessage?: string): string {
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You don't have permission to perform this action.";
  if (status === 404) return "We couldn't find that resource.";
  if (status === 429) return "Too many requests. Please wait a moment and try again.";
  if (status >= 500) return "Something went wrong while connecting to KnowFlow. Please try again.";
  
  if (rawMessage && !rawMessage.includes("http") && !rawMessage.includes("Traceback") && !rawMessage.includes("Exception") && !rawMessage.includes("psycopg2")) {
    return rawMessage;
  }
  return "An unexpected error occurred. Please try again.";
}

export class APIError extends Error {
  status: number;
  data: any;
  userMessage: string;

  constructor(status: number, data: any, rawMessage: string) {
    const safeMsg = getSafeErrorMessage(status, rawMessage);
    super(safeMsg);
    this.name = "APIError";
    this.status = status;
    this.data = data;
    this.userMessage = safeMsg;
  }
}

async function fetchClient<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { timeoutMs = 15000, skipAuth = false, ...init } = options;

  const url = `${BACKEND_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers = new Headers(init.headers);

  // If not FormData, default to JSON
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (!skipAuth) {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      headers.set("Authorization", `Bearer ${session.access_token}`);
    }
  }

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...init,
      headers,
      signal: controller.signal,
    });

    clearTimeout(id);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { detail: response.statusText };
      }

      const rawMsg = errorData?.detail || errorData?.message || `Request failed with status ${response.status}`;
      throw new APIError(
        response.status,
        errorData,
        rawMsg
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null as any;
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(id);
    if (error.name === "AbortError") {
      throw new Error("The request timed out. Please try again.");
    }
    if (error instanceof APIError) {
      throw error;
    }
    throw new Error("KnowFlow is having trouble connecting right now. Please try again.");
  }
}

// -----------------------------------------------------------------------------
// System Health
// -----------------------------------------------------------------------------
export interface HealthData {
  status: "healthy" | "degraded" | "error" | "unconfigured";
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

export async function fetchSystemHealth(): Promise<{
  data: HealthData | null;
  error: string | null;
  latencyMs: number;
}> {
  const start = performance.now();
  try {
    const data = await fetchClient<HealthData>("/api/health", { timeoutMs: 5000 });
    return { data, error: null, latencyMs: Math.round(performance.now() - start) };
  } catch (err: any) {
    const message = err instanceof APIError ? err.message : "Failed to connect to backend service";
    return { data: null, error: message, latencyMs: Math.round(performance.now() - start) };
  }
}

// -----------------------------------------------------------------------------
// Documents
// -----------------------------------------------------------------------------
export interface DocumentItem {
  id: string;
  workspace_id: string;
  title: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  status: "UPLOADED" | "PROCESSING" | "READY" | "FAILED";
  error_message: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  size: number;
}

export async function fetchDocuments(params?: { search?: string; status?: string }): Promise<DocumentListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set("search", params.search);
  if (params?.status && params.status !== "ALL") searchParams.set("status", params.status);

  const query = searchParams.toString();
  return fetchClient<DocumentListResponse>(`/api/v1/documents${query ? `?${query}` : ""}`);
}

export async function uploadDocument(formData: FormData): Promise<{ document: DocumentItem; message: string }> {
  return fetchClient<{ document: DocumentItem; message: string }>("/api/v1/documents/upload", {
    method: "POST",
    body: formData,
    timeoutMs: 60000,
  });
}

export async function deleteDocument(id: string): Promise<void> {
  return fetchClient<void>(`/api/v1/documents/${id}`, { method: "DELETE" });
}

// -----------------------------------------------------------------------------
// Chat & RAG
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
}): Promise<{ data: ChatQueryResponse | null; error?: string }> {
  try {
    const data = await fetchClient<ChatQueryResponse>("/api/v1/chat/query", {
      method: "POST",
      body: JSON.stringify(params),
      timeoutMs: 30000,
    });
    return { data };
  } catch (e: any) {
    return { data: null, error: e.message };
  }
}

export async function fetchConversations(): Promise<{ data: ConversationSummary[] | null; error?: string }> {
  try {
    const data = await fetchClient<ConversationSummary[]>("/api/v1/chat/conversations");
    return { data };
  } catch (e: any) {
    return { data: null, error: e.message };
  }
}

export async function fetchConversationDetail(id: string): Promise<{ data: ConversationDetail | null; error?: string }> {
  try {
    const data = await fetchClient<ConversationDetail>(`/api/v1/chat/conversations/${id}`);
    return { data };
  } catch (e: any) {
    return { data: null, error: e.message };
  }
}

export async function deleteConversation(id: string): Promise<void> {
  return fetchClient<void>(`/api/v1/chat/conversations/${id}`, { method: "DELETE" });
}

// -----------------------------------------------------------------------------
// Search
// -----------------------------------------------------------------------------
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
}): Promise<{ data: SearchResponse | null; error?: string }> {
  const searchParams = new URLSearchParams({ query: params.query });
  if (params.department_id) searchParams.set("department_id", params.department_id);
  if (params.top_k) searchParams.set("top_k", params.top_k.toString());

  try {
    const data = await fetchClient<SearchResponse>(`/api/v1/search?${searchParams.toString()}`);
    return { data };
  } catch (e: any) {
    return { data: null, error: e.message };
  }
}

// -----------------------------------------------------------------------------
// Admin & Feedback (Stubs/Mocks for UI completeness)
// -----------------------------------------------------------------------------
export interface AdminStats {
  total_documents: number;
  total_chunks: number;
  total_conversations: number;
  total_messages: number;
  total_audit_events: number;
  positive_feedback_count: number;
  negative_feedback_count: number;
}

export interface AuditLogRecord {
  id: string;
  created_at: string;
  action: string;
  user_id: string;
  ip_address: string;
  metadata_json: string;
}

export interface EvaluationSummary {
  pass_rate_pct: number;
  passed_cases: number;
  total_cases: number;
  hit_rate_at_1: number;
  hit_rate_at_3: number;
  mrr: number;
  ndcg_at_5: number;
  avg_faithfulness: number;
  avg_latency_ms: number;
  refusal_accuracy_pct: number;
  false_positives: number;
  false_negatives: number;
  case_results: {
    case_id: string;
    question: string;
    category: string;
    hit_at_3: number;
    mrr: number;
    is_out_of_scope: boolean;
    faithfulness_score: number;
    latency_ms: number;
    passed: boolean;
  }[];
}

export async function fetchAdminStats(): Promise<{ data: AdminStats | null; error?: string }> {
  return fetchClient<AdminStats>("/api/admin/stats");
}

export async function fetchAuditLogs(action?: string): Promise<{ data: AuditLogRecord[] | null; error?: string }> {
  const url = action ? `/api/admin/audit?action=${encodeURIComponent(action)}` : "/api/admin/audit";
  return fetchClient<AuditLogRecord[]>(url);
}

export async function triggerEvaluationBenchmark(): Promise<{ data: EvaluationSummary | null; error?: string }> {
  return fetchClient<EvaluationSummary>("/api/admin/evaluations/run", { method: "POST" });
}

export async function submitFeedback(params: { message_id: string; rating: number; category: string }): Promise<{ success: boolean }> {
  const { error } = await fetchClient<{ success: boolean }>("/api/feedback", {
    method: "POST",
    body: JSON.stringify(params),
  });
  return { success: !error };
}

// -----------------------------------------------------------------------------
// Multi-Tenant Workspaces
// -----------------------------------------------------------------------------
export interface Workspace {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export async function createWorkspace(params: { name: string; slug: string }): Promise<{ data: Workspace | null; error?: string }> {
  try {
    const data = await fetchClient<Workspace>("/api/v1/workspaces", {
      method: "POST",
      body: JSON.stringify(params),
    });
    return { data };
  } catch (e: any) {
    return { data: null, error: e.message || "Failed to create workspace" };
  }
}
