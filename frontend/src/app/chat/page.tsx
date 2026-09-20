"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  MessageSquare,
  Bot,
  Send,
  Sparkles,
  ShieldCheck,
  FileText,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  Plus,
  Trash2,
  AlertTriangle,
  Cpu,
} from "lucide-react";
import {
  sendChatQuery,
  fetchConversations,
  fetchConversationDetail,
  deleteConversation,
  submitFeedback,
  ChatMessage,
  ConversationSummary,
} from "@/lib/api";

function ChatContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, number>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation list
  const loadConversations = async () => {
    const res = await fetchConversations();
    if (res.data) {
      setConversations(res.data);
      if (!activeConvId && res.data.length > 0) {
        // select first conversation by default
        loadConversation(res.data[0].id);
      }
    }
  };

  const loadConversation = async (convId: string) => {
    setActiveConvId(convId);
    const res = await fetchConversationDetail(convId);
    if (res.data) {
      setMessages(res.data.messages);
      // Auto-expand sources on assistant messages
      const expanded: Record<string, boolean> = {};
      res.data.messages.forEach((m) => {
        if (m.sources && m.sources.length > 0) expanded[m.id] = true;
      });
      setExpandedSources(expanded);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setInputMessage("");
  };

  const handleDeleteConv = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteConversation(convId);
    if (activeConvId === convId) {
      handleNewChat();
    }
    loadConversations();
  };

  const handleSubmit = async (e?: React.FormEvent, customMsg?: string) => {
    if (e) e.preventDefault();
    const queryText = (customMsg || inputMessage).trim();
    if (!queryText || loading) return;

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConvId || "",
      sender_type: "USER",
      content: queryText,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInputMessage("");
    setLoading(true);

    const res = await sendChatQuery({
      message: queryText,
      conversation_id: activeConvId,
    });

    if (res.data) {
      const { conversation_id, assistant_message_id, answer, citations } = res.data;
      setActiveConvId(conversation_id);

      const assistantMsg: ChatMessage = {
        id: assistant_message_id,
        conversation_id,
        sender_type: "ASSISTANT",
        content: answer,
        created_at: new Date().toISOString(),
        sources: citations,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setExpandedSources((prev) => ({ ...prev, [assistant_message_id]: true }));
      loadConversations();
    } else {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        conversation_id: activeConvId || "",
        sender_type: "ASSISTANT",
        content: `Error: ${res.error || "Failed to process query. Please try again."}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
    setLoading(false);
  };

  const handleFeedback = async (messageId: string, rating: number) => {
    setFeedbackGiven((prev) => ({ ...prev, [messageId]: rating }));
    await submitFeedback({ message_id: messageId, rating, category: "USER_RATING" });
  };

  const toggleSources = (messageId: string) => {
    setExpandedSources((prev) => ({ ...prev, [messageId]: !prev[messageId] }));
  };

  return (
    <div className="max-w-6xl mx-auto flex gap-6 h-[calc(100vh-100px)]">
      {/* Conversations Sidebar */}
      <div className="hidden lg:flex w-64 flex-col rounded-2xl border border-zinc-800/80 bg-zinc-950/60 p-3 space-y-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center space-x-2 rounded-xl bg-indigo-600 px-3 py-2 text-xs font-medium text-white hover:bg-indigo-500 transition-colors shadow-sm"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>New Inquiry</span>
        </button>

        <div className="text-[11px] font-medium text-zinc-500 px-2 uppercase tracking-wider">
          Recent Conversations
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 pr-1">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-zinc-500">No past inquiries</div>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => loadConversation(c.id)}
                className={`group flex items-center justify-between rounded-xl px-3 py-2 text-xs cursor-pointer transition-all ${
                  activeConvId === c.id
                    ? "bg-zinc-800 text-white font-medium"
                    : "text-zinc-400 hover:bg-zinc-900/60 hover:text-zinc-200"
                }`}
              >
                <div className="flex items-center space-x-2 truncate">
                  <MessageSquare className="h-3.5 w-3.5 shrink-0 text-zinc-500" />
                  <span className="truncate">{c.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteConv(c.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-400 p-1"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Stream */}
      <div className="flex-1 flex flex-col rounded-2xl border border-zinc-800/80 bg-zinc-950/40 overflow-hidden">
        {/* Chat Header */}
        <div className="border-b border-zinc-800/80 px-5 py-3.5 flex items-center justify-between bg-zinc-950/80 backdrop-blur-sm">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-emerald-400">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xs font-semibold text-white">KnowFlow Assistant</h2>
                <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.2 text-[9px] font-medium text-emerald-400">
                  Grounded Answering Policy
                </span>
              </div>
              <p className="text-[11px] text-zinc-400">
                Only verified documentation used. Refuses when evidence is insufficient.
              </p>
            </div>
          </div>

          <button
            onClick={handleNewChat}
            className="lg:hidden rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-300"
          >
            New
          </button>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-zinc-700/80 bg-zinc-900 text-indigo-400 shadow-inner">
                <Bot className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-zinc-200">KnowFlow Enterprise Assistant</h3>
                <p className="text-xs text-zinc-400 max-w-md leading-relaxed">
                  Query standard operating procedures, clinical protocols, IT policies, and compliance manuals.
                  Every statement is substantiated by verified document citations.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-lg pt-2 text-left">
                <button
                  onClick={() => handleSubmit(undefined, "What temperature range is required for cold chain storage?")}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 text-xs text-zinc-300 hover:border-indigo-500/40 hover:bg-zinc-900 transition-all flex items-start space-x-2 text-left"
                >
                  <Sparkles className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <span>&ldquo;What temperature range is required for cold chain storage?&rdquo;</span>
                </button>
                <button
                  onClick={() => handleSubmit(undefined, "What is the deadline for reporting a critical deviation?")}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 text-xs text-zinc-300 hover:border-indigo-500/40 hover:bg-zinc-900 transition-all flex items-start space-x-2 text-left"
                >
                  <Sparkles className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <span>&ldquo;What is the deadline for reporting a critical deviation?&rdquo;</span>
                </button>
                <button
                  onClick={() => handleSubmit(undefined, "What are the password complexity requirements?")}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 text-xs text-zinc-300 hover:border-indigo-500/40 hover:bg-zinc-900 transition-all flex items-start space-x-2 text-left"
                >
                  <Sparkles className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <span>&ldquo;What are the password complexity requirements?&rdquo;</span>
                </button>
                <button
                  onClick={() => handleSubmit(undefined, "Who won the 2022 FIFA World Cup?")}
                  className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 text-xs text-zinc-400 hover:border-amber-500/40 hover:bg-zinc-900 transition-all flex items-start space-x-2 text-left"
                >
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <span>&ldquo;Who won the 2022 FIFA World Cup?&rdquo; (Tests Refusal)</span>
                </button>
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender_type === "USER" ? "items-end" : "items-start"}`}
              >
                {/* Message Bubble */}
                <div
                  className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                    m.sender_type === "USER"
                      ? "bg-indigo-600 text-white rounded-br-none shadow-sm"
                      : "bg-zinc-900/80 text-zinc-200 border border-zinc-800/80 rounded-bl-none shadow-sm"
                  }`}
                >
                  {/* Assistant header banner */}
                  {m.sender_type === "ASSISTANT" && (
                    <div className="flex items-center justify-between pb-1 border-b border-zinc-800/60 text-[10px] text-zinc-400">
                      <div className="flex items-center space-x-1.5 text-emerald-400">
                        <ShieldCheck className="h-3 w-3" />
                        <span className="font-medium">Grounded Answering Policy</span>
                      </div>
                      <div className="flex items-center space-x-1 text-zinc-500">
                        <Cpu className="h-2.5 w-2.5" />
                        <span>Verified Synthesis</span>
                      </div>
                    </div>
                  )}

                  {/* Body Text */}
                  <div className="whitespace-pre-wrap font-sans text-xs">{m.content}</div>

                  {/* Verified Sources / Citations Drawer */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-zinc-800/60 space-y-2">
                      <button
                        onClick={() => toggleSources(m.id)}
                        className="flex items-center justify-between w-full text-[11px] font-medium text-indigo-400 hover:text-indigo-300"
                      >
                        <span className="flex items-center space-x-1.5">
                          <FileText className="h-3 w-3" />
                          <span>Verified Sources ({m.sources.length} citations)</span>
                        </span>
                        {expandedSources[m.id] ? (
                          <ChevronUp className="h-3.5 w-3.5" />
                        ) : (
                          <ChevronDown className="h-3.5 w-3.5" />
                        )}
                      </button>

                      {expandedSources[m.id] && (
                        <div className="space-y-2 pt-1">
                          {m.sources.map((cit, idx) => (
                            <div
                              key={cit.id || idx}
                              className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-2.5 text-[11px] space-y-1"
                            >
                              <div className="flex items-center justify-between font-medium text-zinc-200">
                                <span className="truncate">{cit.document_title}</span>
                                <span className="text-zinc-500 font-normal">Page {cit.page_number}</span>
                              </div>
                              {cit.section_heading && (
                                <div className="text-[10px] text-zinc-400 font-mono">
                                  Section: {cit.section_heading}
                                </div>
                              )}
                              <div className="text-[11px] text-zinc-400 italic bg-zinc-900/40 p-1.5 rounded border border-zinc-850">
                                &ldquo;{cit.relevant_text}&rdquo;
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Assistant Footer & Feedback */}
                  {m.sender_type === "ASSISTANT" && (
                    <div className="flex items-center justify-between pt-2 border-t border-zinc-800/40 text-[10px] text-zinc-500">
                      <span>Was this verified answer helpful?</span>
                      <div className="flex items-center space-x-1.5">
                        <button
                          onClick={() => handleFeedback(m.id, 1)}
                          disabled={feedbackGiven[m.id] !== undefined}
                          className={`p-1 rounded hover:bg-zinc-800 ${
                            feedbackGiven[m.id] === 1 ? "text-emerald-400" : "text-zinc-400"
                          }`}
                        >
                          <ThumbsUp className="h-3 w-3" />
                        </button>
                        <button
                          onClick={() => handleFeedback(m.id, -1)}
                          disabled={feedbackGiven[m.id] !== undefined}
                          className={`p-1 rounded hover:bg-zinc-800 ${
                            feedbackGiven[m.id] === -1 ? "text-red-400" : "text-zinc-400"
                          }`}
                        >
                          <ThumbsDown className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex items-center space-x-2 text-xs text-zinc-400 bg-zinc-900/50 p-3 rounded-xl border border-zinc-800/60 w-fit">
              <div className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
              <span>Searching authorized SOPs and evaluating grounding evidence...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="border-t border-zinc-800/80 p-3.5 bg-zinc-950/80">
          <form onSubmit={handleSubmit} className="flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about SOP deviations, cold chain limits, leave guidelines, IT access..."
              className="flex-1 rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:border-indigo-500/60 focus:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-indigo-500/30"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-medium text-white hover:bg-indigo-500 disabled:opacity-40 flex items-center space-x-1.5 transition-colors"
            >
              <span>Query</span>
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function AskAIPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-zinc-400">Loading AI Assistant...</div>}>
      <ChatContent />
    </Suspense>
  );
}
