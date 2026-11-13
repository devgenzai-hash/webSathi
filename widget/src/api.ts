import { WidgetConfig, ChatHistoryResponse, ChatMessage, ChatResponse, WidgetConfigResponse } from './types';

const DEFAULT_API_URL = 'https://api.makewebsiteaiready.com';
const MAX_STORED_MESSAGES = 100;
const memoryStorage: Record<string, string> = {};

export class ChatbotAPI {
  private siteKey: string;
  private apiUrl: string;
  private sessionId: string | null = null;
  private visitorId: string;
  private storageScope: string;

  constructor(config: WidgetConfig) {
    this.siteKey = config.siteKey;
    this.apiUrl = (config.apiUrl || DEFAULT_API_URL).replace(/\/+$/, '');
    this.storageScope = this.getStorageScope();
    this.visitorId = this.getOrCreateVisitorId();
    this.sessionId = this.readStorage('session_id');
  }

  private getOrCreateVisitorId(): string {
    const key = 'visitor_id';
    let id = this.readStorage(key);
    if (!id) {
      id = this.createId('v');
      this.writeStorage(key, id);
    }
    return id;
  }

  private createId(prefix: string): string {
    const cryptoApi = typeof crypto !== 'undefined' ? crypto : undefined;
    if (cryptoApi?.randomUUID) {
      return `${prefix}_${cryptoApi.randomUUID()}`;
    }

    return `${prefix}_${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
  }

  private getStorageScope(): string {
    const siteKey = this.siteKey.replace(/[^a-zA-Z0-9_-]/g, '_');
    const host = this.getCurrentHost().replace(/[^a-zA-Z0-9_.:-]/g, '_');
    return `mwair:${siteKey}:${host}`;
  }

  private getCurrentHost(): string {
    if (typeof window === 'undefined') return 'unknown-host';

    const hostname = window.location.hostname || 'unknown-host';
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${hostname}${port}`.toLowerCase();
  }

  private getPageUrl(): string | undefined {
    if (typeof window === 'undefined') return undefined;
    return window.location.href;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = { 'X-Site-Key': this.siteKey };
    if (typeof window !== 'undefined') {
      if (window.location.origin && window.location.origin !== 'null') {
        headers['X-Widget-Origin'] = window.location.origin;
      }
      headers['X-Widget-Page'] = window.location.href;
    }
    return headers;
  }

  private storageKey(key: string): string {
    return `${this.storageScope}:${key}`;
  }

  private readStorage(key: string): string | null {
    const scopedKey = this.storageKey(key);
    try {
      if (typeof window === 'undefined') return memoryStorage[scopedKey] ?? null;
      return window.localStorage.getItem(scopedKey) ?? memoryStorage[scopedKey] ?? null;
    } catch {
      return memoryStorage[scopedKey] ?? null;
    }
  }

  private writeStorage(key: string, value: string): void {
    const scopedKey = this.storageKey(key);
    memoryStorage[scopedKey] = value;
    try {
      if (typeof window === 'undefined') return;
      window.localStorage.setItem(scopedKey, value);
    } catch {
      // In private browsing or locked-down embeds, memory storage still works for this page lifetime.
    }
  }

  private removeStorage(key: string): void {
    const scopedKey = this.storageKey(key);
    delete memoryStorage[scopedKey];
    try {
      if (typeof window === 'undefined') return;
      window.localStorage.removeItem(scopedKey);
    } catch {
      // Ignore storage failures.
    }
  }

  async getWidgetConfig(): Promise<WidgetConfigResponse> {
    const response = await fetch(`${this.apiUrl}/api/v1/chat/config`, {
      headers: this.getHeaders(),
    });
    if (!response.ok) throw new Error(await this.getErrorMessage(response, 'Failed to fetch widget config'));
    return response.json();
  }

  async getHistory(): Promise<ChatHistoryResponse> {
    const params = new URLSearchParams({ visitor_id: this.visitorId });
    if (this.sessionId) params.set('session_id', this.sessionId);

    const response = await fetch(`${this.apiUrl}/api/v1/chat/history?${params.toString()}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) throw new Error(await this.getErrorMessage(response, 'Failed to fetch chat history'));

    const data: ChatHistoryResponse = await response.json();
    if (data.session_id) {
      this.sessionId = data.session_id;
      this.writeStorage('session_id', data.session_id);
    }

    return data;
  }

  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await fetch(`${this.apiUrl}/api/v1/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getHeaders(),
      },
      body: JSON.stringify({
        message,
        session_id: this.sessionId,
        visitor_id: this.visitorId,
        page_url: this.getPageUrl(),
      }),
    });

    if (!response.ok) {
      throw new Error(await this.getErrorMessage(response, 'Failed to send message'));
    }

    const data: ChatResponse = await response.json();
    this.sessionId = data.session_id;
    this.writeStorage('session_id', data.session_id);
    return data;
  }

  loadMessages(): ChatMessage[] {
    const stored = this.readStorage('messages');
    if (!stored) return [];

    try {
      const parsed = JSON.parse(stored) as ChatMessage[];
      if (!Array.isArray(parsed)) return [];

      return parsed
        .filter((message) => (message.role === 'user' || message.role === 'assistant') && typeof message.content === 'string')
        .slice(-MAX_STORED_MESSAGES)
        .map((message) => ({
          role: message.role,
          content: message.content,
          timestamp: message.timestamp ? new Date(message.timestamp) : new Date(),
        }));
    } catch {
      this.removeStorage('messages');
      return [];
    }
  }

  saveMessages(messages: ChatMessage[]): void {
    const serializable = messages.slice(-MAX_STORED_MESSAGES).map((message) => ({
      role: message.role,
      content: message.content,
      timestamp: message.timestamp instanceof Date ? message.timestamp.toISOString() : new Date(message.timestamp).toISOString(),
    }));
    this.writeStorage('messages', JSON.stringify(serializable));
  }

  async captureLead(email: string, question?: string): Promise<void> {
    await fetch(`${this.apiUrl}/api/v1/chat/capture-lead`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.getHeaders() },
      body: JSON.stringify({
        email,
        question: question || null,
        session_id: this.sessionId,
        visitor_id: this.visitorId,
        page_url: this.getPageUrl(),
      }),
    });
    // Fire-and-forget — ignore response errors so the widget never breaks.
  }

  resetSession(): void {
    this.sessionId = null;
    this.removeStorage('session_id');
    this.removeStorage('messages');
  }

  private async getErrorMessage(response: Response, fallback: string): Promise<string> {
    try {
      const data = await response.json();
      if (typeof data.detail === 'string') return data.detail;
    } catch {
      // Fall through to status text.
    }

    return response.statusText ? `${fallback}: ${response.statusText}` : fallback;
  }
}
