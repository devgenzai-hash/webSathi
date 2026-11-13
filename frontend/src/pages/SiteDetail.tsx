import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Upload, FileText, Trash2, Copy, Check, Globe, Plus, Pause, Play } from "lucide-react";
import {
  sitesAPI, documentsAPI, modelsAPI,
  conversationsAPI, leadsAPI, crawlerAPI, variantsAPI, auditAPI,
} from "../services/api";

interface Site {
  id: string; site_name: string; domain: string; site_key: string;
  is_verified: boolean; model_provider: string; model_name: string;
  system_prompt: string; max_tokens: number; temperature: number;
  widget_position: string; widget_color: string; widget_title: string;
  widget_welcome_message: string;
  hide_branding: boolean; monthly_query_limit: number; user_openai_key: string | null;
  recrawl_interval_hours: number; webhook_url: string | null; ab_testing_enabled: boolean;
}
interface Document {
  id: string; filename: string; file_type: string; file_size: number;
  chunk_count: number; status: string; created_at: string;
}
interface ModelOption { provider: string; model_id: string; display_name: string; pricing_tier: string; }
interface Conversation {
  session_id: string; visitor_id: string; message_count: number;
  last_message_at: string; has_unanswered: boolean; has_negative_sentiment: boolean;
}
interface ConversationMessage {
  id: string; role: string; content: string; was_answered: boolean;
  confidence: string; sentiment: string; created_at: string;
}
interface ConversationDetail {
  session_id: string; visitor_id: string; messages: ConversationMessage[];
  created_at: string; last_message_at: string;
}
interface UnansweredQuestion {
  message_id: string; session_id: string; visitor_id: string;
  question: string; created_at: string;
}
interface Lead { id: string; email: string; visitor_id: string; question: string | null; created_at: string; }
interface CrawlJob {
  id: string; root_url: string; status: string; pages_crawled: number;
  error_message: string | null; created_at: string;
}
interface PromptVariant {
  id: string; name: string; system_prompt: string; is_control: boolean;
  is_active: boolean; total_chats: number; answered_count: number;
}
interface AuditEntry { id: string; action: string; detail: string | null; ip_address: string | null; created_at: string; }
interface UsageStats {
  total_messages: number; total_documents: number; monthly_query_count: number;
  monthly_query_limit: number; billing_enabled: boolean; period: string;
}

const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const widgetUrl = (import.meta as any).env?.VITE_WIDGET_URL
  || (isLocalHost ? "http://localhost:3000/widget/dist/chatbot-widget.js" : "https://cdn.makewebsiteaiready.com/chatbot-widget.js");
const widgetApiUrl = (import.meta as any).env?.VITE_WIDGET_API_URL || (isLocalHost ? "http://localhost:8000" : "");

function getEmbedCode(site: Site) {
  const apiLine = widgetApiUrl ? `\n  data-api-url="${widgetApiUrl}"` : "";
  return `<script\n  src="${widgetUrl}"\n  data-site-key="${site.site_key}"${apiLine}\n></script>`;
}

const statusBadge = (s: string) => {
  const cls = s === "ready" || s === "done" ? "bg-green-100 text-green-700"
    : s === "processing" || s === "running" ? "bg-blue-100 text-blue-700"
    : "bg-red-100 text-red-700";
  return <span className={`ml-2 px-1.5 py-0.5 rounded text-xs ${cls}`}>{s}</span>;
};

type Tab = "documents" | "crawler" | "conversations" | "leads" | "unanswered"
         | "ab_tests" | "usage" | "settings" | "audit" | "embed";

const TABS: { id: Tab; label: string }[] = [
  { id: "documents",     label: "Documents"    },
  { id: "crawler",       label: "Crawler"      },
  { id: "conversations", label: "Conversations"},
  { id: "leads",         label: "Leads"        },
  { id: "unanswered",    label: "Unanswered"   },
  { id: "ab_tests",      label: "A/B Tests"    },
  { id: "usage",         label: "Usage"        },
  { id: "settings",      label: "Settings"     },
  { id: "audit",         label: "Audit"        },
  { id: "embed",         label: "Embed"        },
];

export default function SiteDetail() {
  const { siteId } = useParams<{ siteId: string }>();
  const [site,            setSite]            = useState<Site | null>(null);
  const [documents,       setDocuments]       = useState<Document[]>([]);
  const [models,          setModels]          = useState<ModelOption[]>([]);
  const [uploading,       setUploading]       = useState(false);
  const [copied,          setCopied]          = useState(false);
  const [activeTab,       setActiveTab]       = useState<Tab>("documents");
  const [conversations,   setConversations]   = useState<Conversation[]>([]);
  const [openConv,        setOpenConv]        = useState<ConversationDetail | null>(null);
  const [unanswered,      setUnanswered]      = useState<UnansweredQuestion[]>([]);
  const [leads,           setLeads]           = useState<Lead[]>([]);
  const [crawlJobs,       setCrawlJobs]       = useState<CrawlJob[]>([]);
  const [crawlUrl,        setCrawlUrl]        = useState("");
  const [crawling,        setCrawling]        = useState(false);
  const [variants,        setVariants]        = useState<PromptVariant[]>([]);
  const [newVarName,      setNewVarName]      = useState("");
  const [newVarPrompt,    setNewVarPrompt]    = useState("");
  const [auditLogs,       setAuditLogs]       = useState<AuditEntry[]>([]);
  const [usage,           setUsage]           = useState<UsageStats | null>(null);

  useEffect(() => {
    if (siteId) { loadSite(); loadDocuments(); loadModels(); }
  }, [siteId]);

  useEffect(() => {
    if (!siteId) return;
    if (activeTab === "conversations") conversationsAPI.list(siteId).then(r => setConversations(r.data)).catch(() => {});
    if (activeTab === "unanswered")    conversationsAPI.unanswered(siteId).then(r => setUnanswered(r.data)).catch(() => {});
    if (activeTab === "leads")         leadsAPI.list(siteId).then(r => setLeads(r.data)).catch(() => {});
    if (activeTab === "crawler")       crawlerAPI.list(siteId).then(r => setCrawlJobs(r.data)).catch(() => {});
    if (activeTab === "ab_tests")      variantsAPI.list(siteId).then(r => setVariants(r.data)).catch(() => {});
    if (activeTab === "audit")         auditAPI.forSite(siteId).then(r => setAuditLogs(r.data)).catch(() => {});
    if (activeTab === "usage")         conversationsAPI.usage(siteId).then(r => setUsage(r.data)).catch(() => {});
  }, [activeTab, siteId]);

  const loadSite      = () => sitesAPI.get(siteId!).then(r => setSite(r.data));
  const loadDocuments = () => documentsAPI.list(siteId!).then(r => setDocuments(r.data));
  const loadModels    = () => modelsAPI.list().then(r => setModels(r.data.models)).catch(() => {});

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) await documentsAPI.upload(siteId!, file);
      loadDocuments();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Upload failed");
    } finally { setUploading(false); e.target.value = ""; }
  };

  const handleDeleteDoc = async (docId: string) => {
    if (!confirm("Delete this document?")) return;
    await documentsAPI.delete(siteId!, docId);
    loadDocuments();
  };

  const handleUpdate = async (data: Record<string, unknown>) => {
    await sitesAPI.update(siteId!, data);
    loadSite();
  };

  const copyEmbed = () => {
    if (!site) return;
    navigator.clipboard.writeText(getEmbedCode(site));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleStartCrawl = async () => {
    if (!crawlUrl.trim()) return;
    setCrawling(true);
    try {
      await crawlerAPI.start(siteId!, crawlUrl.trim());
      crawlerAPI.list(siteId!).then(r => setCrawlJobs(r.data));
      setCrawlUrl("");
    } catch (err: any) {
      alert(err.response?.data?.detail || "Crawl failed");
    } finally { setCrawling(false); }
  };

  const handleAddVariant = async () => {
    if (!newVarName || !newVarPrompt) return;
    await variantsAPI.create(siteId!, { name: newVarName, system_prompt: newVarPrompt });
    variantsAPI.list(siteId!).then(r => setVariants(r.data));
    setNewVarName(""); setNewVarPrompt("");
  };

  if (!site) return (
    <div className="flex justify-center py-12">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
    </div>
  );

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{site.site_name}</h1>
        <p className="text-gray-500">{site.domain}</p>
      </div>

      {/* Tab bar */}
      <div className="flex flex-wrap gap-1 bg-gray-100 rounded-lg p-1 mb-6">
        {TABS.map(({ id, label }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === id ? "bg-white shadow text-primary-700" : "text-gray-600 hover:text-gray-900"
            }`}>
            {label}
          </button>
        ))}
      </div>

      {/* ── Documents ─────────────────────────────────────── */}
      {activeTab === "documents" && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Documents</h2>
            <label className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 cursor-pointer">
              <Upload size={18} />
              {uploading ? "Uploading..." : "Upload"}
              <input type="file" multiple accept=".pdf,.docx,.txt,.csv,.png,.jpg,.jpeg,.webp"
                onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
          {documents.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <FileText size={40} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">No documents yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map(doc => (
                <div key={doc.id} className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText size={20} className="text-primary-500" />
                    <div>
                      <p className="font-medium text-sm">{doc.filename}</p>
                      <p className="text-xs text-gray-400">
                        {doc.file_type.toUpperCase()} · {(doc.file_size / 1024).toFixed(1)} KB · {doc.chunk_count} chunks
                        {statusBadge(doc.status)}
                      </p>
                    </div>
                  </div>
                  <button onClick={() => handleDeleteDoc(doc.id)} className="text-red-400 hover:text-red-600 p-2">
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Crawler ───────────────────────────────────────── */}
      {activeTab === "crawler" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-1">Web Crawler</h2>
            <p className="text-sm text-gray-500 mb-4">
              Paste a URL. The crawler visits every page on that domain and adds the text to your knowledge base.
            </p>
            <div className="flex gap-2">
              <input type="url" value={crawlUrl} onChange={e => setCrawlUrl(e.target.value)}
                placeholder="https://example.com"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm" />
              <button onClick={handleStartCrawl} disabled={crawling || !crawlUrl.trim()}
                className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50">
                <Globe size={16} />{crawling ? "Starting..." : "Crawl"}
              </button>
            </div>
          </div>
          {crawlJobs.map(job => (
            <div key={job.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium truncate max-w-md">{job.root_url}</p>
                {statusBadge(job.status)}
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {job.pages_crawled} pages · {new Date(job.created_at).toLocaleString()}
              </p>
              {job.error_message && <p className="text-xs text-red-500 mt-1">{job.error_message}</p>}
            </div>
          ))}
        </div>
      )}

      {/* ── Conversations ─────────────────────────────────── */}
      {activeTab === "conversations" && (
        <div className="space-y-4">
          {openConv ? (
            <div>
              <button onClick={() => setOpenConv(null)} className="text-sm text-primary-600 mb-3 hover:underline">
                ← Back
              </button>
              <p className="text-xs text-gray-400 mb-3">Visitor: {openConv.visitor_id}</p>
              <div className="space-y-3">
                {openConv.messages.map(msg => (
                  <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-prose rounded-xl px-4 py-2 text-sm ${
                      msg.role === "user" ? "bg-primary-100 text-primary-900" : "bg-gray-100 text-gray-800"
                    }`}>
                      <p>{msg.content}</p>
                      {msg.role === "assistant" && !msg.was_answered &&
                        <p className="text-xs text-red-500 mt-1">⚠ not answered</p>}
                      {msg.role === "assistant" && msg.confidence !== "high" &&
                        <p className="text-xs text-yellow-600 mt-1">{msg.confidence} confidence</p>}
                      {msg.role === "user" && msg.sentiment === "negative" &&
                        <p className="text-xs text-red-500 mt-1">😠 negative</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              <h2 className="text-lg font-semibold">Conversations</h2>
              {conversations.length === 0
                ? <p className="text-gray-400 text-sm">No conversations yet.</p>
                : (
                  <div className="space-y-2">
                    {conversations.map(c => (
                      <button key={c.session_id}
                        onClick={() => conversationsAPI.get(siteId!, c.session_id).then(r => setOpenConv(r.data))}
                        className="w-full bg-white rounded-lg border border-gray-200 p-4 text-left hover:border-primary-300">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium">{c.visitor_id.slice(0, 16)}...</p>
                          <div className="flex gap-2">
                            {c.has_unanswered &&
                              <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">unanswered</span>}
                            {c.has_negative_sentiment &&
                              <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">😠</span>}
                            <span className="text-xs text-gray-400">{c.message_count} msgs</span>
                          </div>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{new Date(c.last_message_at).toLocaleString()}</p>
                      </button>
                    ))}
                  </div>
                )
              }
            </>
          )}
        </div>
      )}

      {/* ── Leads ─────────────────────────────────────────── */}
      {activeTab === "leads" && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Captured Leads</h2>
          <p className="text-sm text-gray-500">Emails collected when the bot could not answer a question.</p>
          {leads.length === 0
            ? <p className="text-gray-400 text-sm">No leads yet.</p>
            : (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 text-left text-gray-500 text-xs uppercase">
                      <th className="px-4 py-3">Email</th>
                      <th className="px-4 py-3">Question</th>
                      <th className="px-4 py-3">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map(l => (
                      <tr key={l.id} className="border-t border-gray-100">
                        <td className="px-4 py-3 font-medium">{l.email}</td>
                        <td className="px-4 py-3 text-gray-500 max-w-sm truncate">{l.question || "—"}</td>
                        <td className="px-4 py-3 text-gray-400 whitespace-nowrap">
                          {new Date(l.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          }
        </div>
      )}

      {/* ── Unanswered ────────────────────────────────────── */}
      {activeTab === "unanswered" && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Unanswered Questions</h2>
          <p className="text-sm text-gray-500">Upload more documents to fill these gaps.</p>
          {unanswered.length === 0
            ? <p className="text-gray-400 text-sm">No unanswered questions. 🎉</p>
            : (
              <div className="space-y-2">
                {unanswered.map(q => (
                  <div key={q.message_id} className="bg-white rounded-lg border border-yellow-200 p-4">
                    <p className="text-sm font-medium">"{q.question}"</p>
                    <p className="text-xs text-gray-400 mt-1">{new Date(q.created_at).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            )
          }
        </div>
      )}

      {/* ── A/B Tests ─────────────────────────────────────── */}
      {activeTab === "ab_tests" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">A/B Prompt Testing</h2>
              <p className="text-sm text-gray-500">Create variants. Enable the toggle to randomly serve them per session.</p>
            </div>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <span className="text-gray-600">A/B Testing</span>
              <input type="checkbox" checked={site.ab_testing_enabled}
                onChange={e => handleUpdate({ ab_testing_enabled: e.target.checked })}
                className="w-4 h-4" />
            </label>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
            <h3 className="font-medium text-sm">Add Variant</h3>
            <input type="text" value={newVarName} onChange={e => setNewVarName(e.target.value)}
              placeholder="Variant name" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <textarea value={newVarPrompt} onChange={e => setNewVarPrompt(e.target.value)}
              placeholder="System prompt for this variant..." rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <button onClick={handleAddVariant} disabled={!newVarName || !newVarPrompt}
              className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50">
              <Plus size={14} /> Add
            </button>
          </div>

          {variants.map(v => (
            <div key={v.id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{v.name}</span>
                  {v.is_control &&
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">control</span>}
                  {!v.is_active &&
                    <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">paused</span>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => variantsAPI.update(siteId!, v.id, { is_active: !v.is_active })
                    .then(() => variantsAPI.list(siteId!).then(r => setVariants(r.data)))}
                    className="p-1.5 text-gray-400 hover:text-gray-600">
                    {v.is_active ? <Pause size={14} /> : <Play size={14} />}
                  </button>
                  <button onClick={() => {
                    if (!confirm("Delete variant?")) return;
                    variantsAPI.delete(siteId!, v.id).then(() => setVariants(prev => prev.filter(x => x.id !== v.id)));
                  }} className="p-1.5 text-red-400 hover:text-red-600">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-400">
                {v.total_chats} chats · {v.total_chats > 0
                  ? Math.round((v.answered_count / v.total_chats) * 100) : 0}% answered
              </p>
            </div>
          ))}
        </div>
      )}

      {/* ── Usage ─────────────────────────────────────────── */}
      {activeTab === "usage" && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Usage</h2>
          {usage ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { label: "Total messages",     value: String(usage.total_messages) },
                  { label: "Documents",          value: String(usage.total_documents) },
                  { label: "Queries this month", value: `${usage.monthly_query_count} / ${usage.monthly_query_limit}` },
                  { label: "Billing",            value: usage.billing_enabled ? "Enabled" : "Disabled" },
                  { label: "Period",             value: usage.period },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-white rounded-xl border border-gray-200 p-5">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
                    <p className="text-2xl font-bold">{value}</p>
                  </div>
                ))}
              </div>
              {!usage.billing_enabled && (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
                  Billing is <strong>disabled</strong>. Set <code>BILLING_ENABLED=true</code> in{" "}
                  <code>backend/.env</code> to enforce monthly query limits.
                </div>
              )}
            </>
          ) : <p className="text-gray-400 text-sm">Loading...</p>}
        </div>
      )}

      {/* ── Settings ──────────────────────────────────────── */}
      {activeTab === "settings" && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Registered Domain</label>
            <input type="text" defaultValue={site.domain}
              onBlur={e => handleUpdate({ domain: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
            <select value={`${site.model_provider}:${site.model_name}`}
              onChange={e => {
                const [p, m] = e.target.value.split(":");
                handleUpdate({ model_provider: p, model_name: m });
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg">
              {models.map(m => (
                <option key={`${m.provider}:${m.model_id}`} value={`${m.provider}:${m.model_id}`}>
                  {m.display_name} ({m.pricing_tier})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Widget Title</label>
            <input type="text" defaultValue={site.widget_title}
              onBlur={e => handleUpdate({ widget_title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Welcome Message</label>
            <input type="text" defaultValue={site.widget_welcome_message}
              onBlur={e => handleUpdate({ widget_welcome_message: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <input type="color" defaultValue={site.widget_color}
                onChange={e => handleUpdate({ widget_color: e.target.value })}
                className="w-16 h-10 border border-gray-300 rounded-lg cursor-pointer" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Position</label>
              <select defaultValue={site.widget_position}
                onChange={e => handleUpdate({ widget_position: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="bottom-right">Bottom Right</option>
                <option value="bottom-left">Bottom Left</option>
                <option value="top-right">Top Right</option>
                <option value="top-left">Top Left</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
            <textarea defaultValue={site.system_prompt}
              onBlur={e => handleUpdate({ system_prompt: e.target.value })}
              rows={4} className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm" />
          </div>

          <hr />
          <h3 className="font-medium text-gray-800">Branding &amp; Billing</h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Hide branding</p>
              <p className="text-xs text-gray-400">Remove "Powered by" badge from the widget.</p>
            </div>
            <input type="checkbox" checked={site.hide_branding}
              onChange={e => handleUpdate({ hide_branding: e.target.checked })} className="w-4 h-4" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Monthly query limit</label>
            <input type="number" defaultValue={site.monthly_query_limit} min={1}
              onBlur={e => handleUpdate({ monthly_query_limit: parseInt(e.target.value) })}
              className="w-40 px-4 py-2 border border-gray-300 rounded-lg" />
            <p className="text-xs text-gray-400 mt-1">Only enforced when BILLING_ENABLED=true in .env</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Your OpenAI key (BYOK)</label>
            <input type="password" defaultValue={site.user_openai_key || ""}
              onBlur={e => handleUpdate({ user_openai_key: e.target.value || null })}
              placeholder="sk-... leave blank to use server key"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm" />
          </div>

          <hr />
          <h3 className="font-medium text-gray-800">Crawler &amp; Integrations</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Re-crawl interval (hours, 0 = off)</label>
            <input type="number" defaultValue={site.recrawl_interval_hours} min={0}
              onBlur={e => handleUpdate({ recrawl_interval_hours: parseInt(e.target.value) })}
              className="w-40 px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Webhook URL (Zapier / CRM)</label>
            <input type="url" defaultValue={site.webhook_url || ""}
              onBlur={e => handleUpdate({ webhook_url: e.target.value || null })}
              placeholder="https://hooks.zapier.com/..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm" />
            <p className="text-xs text-gray-400 mt-1">Fired on every lead capture when INTEGRATIONS_ENABLED=true</p>
          </div>
        </div>
      )}

      {/* ── Audit ─────────────────────────────────────────── */}
      {activeTab === "audit" && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Audit Log</h2>
          {auditLogs.length === 0
            ? <p className="text-gray-400 text-sm">No audit entries yet.</p>
            : (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 text-left text-gray-500 text-xs uppercase">
                      <th className="px-4 py-3">Action</th>
                      <th className="px-4 py-3">Detail</th>
                      <th className="px-4 py-3">IP</th>
                      <th className="px-4 py-3">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map(log => (
                      <tr key={log.id} className="border-t border-gray-100">
                        <td className="px-4 py-3 font-mono text-xs text-primary-700">{log.action}</td>
                        <td className="px-4 py-3 text-gray-500 max-w-xs truncate">{log.detail || "—"}</td>
                        <td className="px-4 py-3 text-gray-400">{log.ip_address || "—"}</td>
                        <td className="px-4 py-3 text-gray-400 whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          }
        </div>
      )}

      {/* ── Embed ─────────────────────────────────────────── */}
      {activeTab === "embed" && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold mb-2">Embed Code</h3>
          <p className="text-sm text-gray-500 mb-4">Add this before <code>&lt;/body&gt;</code>:</p>
          <div className="relative">
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto">
              {getEmbedCode(site)}
            </pre>
            <button onClick={copyEmbed}
              className="absolute top-3 right-3 bg-gray-700 text-white p-2 rounded hover:bg-gray-600">
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Site Key:</strong>{" "}
              <code className="bg-blue-100 px-2 py-0.5 rounded">{site.site_key}</code>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
