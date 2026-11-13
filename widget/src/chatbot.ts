import { WidgetConfig, ChatMessage } from './types';
import { ChatbotAPI } from './api';
import { getStyles } from './styles';

export class ChatbotWidget {
  private config: WidgetConfig;
  private api: ChatbotAPI;
  private container: HTMLElement | null = null;
  private toggleWrap: HTMLElement | null = null;
  private chatWindow: HTMLElement | null = null;
  private messagesContainer: HTMLElement | null = null;
  private toggleBtn: HTMLButtonElement | null = null;
  private hideBtn: HTMLButtonElement | null = null;
  private isOpen = false;
  private messages: ChatMessage[] = [];
  private isLoading = false;
  private hideBranding = false;
  private lastUserMessage = '';

  constructor(config: WidgetConfig) {
    this.config = {
      position: 'bottom-right',
      color: '#6366f1',
      title: 'AI Assistant',
      welcomeMessage: 'Hello! How can I help you today?',
      opacity: 1,
      size: 'medium',
      hidden: false,
      ...config,
    };
    this.api = new ChatbotAPI(this.config);
  }

  async init(): Promise<void> {
    // Try to fetch remote config
    try {
      const remoteConfig = await this.api.getWidgetConfig();
      this.config.position = (remoteConfig.widget_position as any) || this.config.position;
      this.config.color = remoteConfig.widget_color || this.config.color;
      this.config.title = remoteConfig.widget_title || this.config.title;
      this.config.welcomeMessage = remoteConfig.widget_welcome_message || this.config.welcomeMessage;
      this.hideBranding = remoteConfig.hide_branding ?? false;
    } catch (e) {
      // Use local config if remote fails
    }

    this.messages = this.api.loadMessages();
    if (this.messages.length === 0) {
      try {
        const history = await this.api.getHistory();
        this.messages = history.messages.map((message) => ({
          role: message.role,
          content: message.content,
          timestamp: new Date(message.created_at || message.timestamp || Date.now()),
        }));
        this.api.saveMessages(this.messages);
      } catch (e) {
        // Start fresh if history is unavailable; send errors are shown in-chat.
      }
    }

    this.injectStyles();
    this.render();

    if (!this.config.hidden) {
      this.show();
    }
  }

  private injectStyles(): void {
    const styleEl = document.createElement('style');
    styleEl.id = 'mwair-styles';
    styleEl.textContent = getStyles(this.config.color!, this.config.position!);
    document.head.appendChild(styleEl);
  }

  private render(): void {
    // Create toggle button with a small hide control
    this.toggleWrap = document.createElement('div');
    this.toggleWrap.className = 'mwair-toggle-wrap';

    this.toggleBtn = document.createElement('button');
    this.toggleBtn.className = 'mwair-toggle-btn';
    this.toggleBtn.type = 'button';
    this.toggleBtn.setAttribute('aria-label', 'Open chat');
    this.toggleBtn.innerHTML = `
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
    `;
    this.toggleBtn.onclick = () => this.toggle();

    this.hideBtn = document.createElement('button');
    this.hideBtn.className = 'mwair-hide-widget-btn';
    this.hideBtn.type = 'button';
    this.hideBtn.title = 'Hide chat widget';
    this.hideBtn.setAttribute('aria-label', 'Hide chat widget');
    this.hideBtn.innerHTML = '&times;';
    this.hideBtn.onclick = (event) => {
      event.stopPropagation();
      this.hide();
    };

    this.toggleWrap.appendChild(this.toggleBtn);
    this.toggleWrap.appendChild(this.hideBtn);
    document.body.appendChild(this.toggleWrap);

    // Create chat window
    this.chatWindow = document.createElement('div');
    this.chatWindow.className = 'mwair-chat-window';
    this.chatWindow.innerHTML = `
      <div class="mwair-chat-header">
        <h3>${this.escapeHtml(this.config.title!)}</h3>
        <div class="mwair-header-actions">
          <button class="mwair-header-btn mwair-minimize-btn" title="Minimize">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 13H5v-2h14v2z"/>
            </svg>
          </button>
          <button class="mwair-header-btn mwair-close-btn" title="Close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="mwair-chat-messages"></div>
      <div class="mwair-chat-input">
        <input type="text" placeholder="Type your message..." />
        <button>Send</button>
      </div>
      <div class="mwair-powered-by" id="mwair-powered-by">
        Powered by <a href="https://makewebsiteaiready.com" target="_blank">MakeWebsiteAIReady</a>
      </div>
    `;
    document.body.appendChild(this.chatWindow);

    // Get references
    this.messagesContainer = this.chatWindow.querySelector('.mwair-chat-messages');
    const input = this.chatWindow.querySelector('.mwair-chat-input input') as HTMLInputElement;
    const sendBtn = this.chatWindow.querySelector('.mwair-chat-input button') as HTMLButtonElement;
    const closeBtn = this.chatWindow.querySelector('.mwair-close-btn') as HTMLButtonElement;
    const minimizeBtn = this.chatWindow.querySelector('.mwair-minimize-btn') as HTMLButtonElement;

    // Event listeners
    sendBtn.onclick = () => this.handleSend(input, sendBtn);
    input.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSend(input, sendBtn);
      }
    };
    closeBtn.onclick = () => this.close();
    minimizeBtn.onclick = () => this.close();

    // Add restored history or the initial welcome message
    if (this.messages.length > 0) {
      this.renderMessages();
    } else if (this.config.welcomeMessage) {
      this.addMessage('assistant', this.config.welcomeMessage);
    }

    // Branding toggle
    if (this.hideBranding) {
      const brandingEl = this.chatWindow!.querySelector('#mwair-powered-by') as HTMLElement | null;
      if (brandingEl) brandingEl.style.display = 'none';
    }

    // Set opacity
    if (this.config.opacity !== undefined && this.config.opacity < 1) {
      this.chatWindow.style.opacity = String(this.config.opacity);
      this.toggleWrap!.style.opacity = String(this.config.opacity);
    }
  }

  private async handleSend(input: HTMLInputElement, sendBtn: HTMLButtonElement): Promise<void> {
    const message = input.value.trim();
    if (!message || this.isLoading) return;

    this.lastUserMessage = message;
    input.value = '';
    this.addMessage('user', message);
    this.showTyping();
    this.isLoading = true;
    sendBtn.disabled = true;

    try {
      const response = await this.api.sendMessage(message);
      this.hideTyping();
      this.addMessage('assistant', response.response);
      // Show email capture when the bot couldn't answer well
      if (response.confidence === 'low' || response.was_answered === false) {
        this.showLeadCapture(message);
      }
    } catch (error) {
      this.hideTyping();
      const errorMessage = this.getDisplayErrorMessage(error);
      this.addMessage('assistant', errorMessage);
    } finally {
      this.isLoading = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  private showLeadCapture(question: string): void {
    if (!this.messagesContainer) return;
    // Remove any existing lead-capture form first
    this.messagesContainer.querySelector('.mwair-lead-capture')?.remove();

    const form = document.createElement('div');
    form.className = 'mwair-lead-capture';
    form.innerHTML = `
      <p class="mwair-lead-title">Want a more detailed answer?</p>
      <p class="mwair-lead-sub">Leave your email and we'll follow up.</p>
      <input type="email" class="mwair-lead-email" placeholder="your@email.com" />
      <div class="mwair-lead-actions">
        <button class="mwair-lead-submit">Notify me</button>
        <button class="mwair-lead-dismiss">No thanks</button>
      </div>
    `;

    const emailInput  = form.querySelector('.mwair-lead-email')   as HTMLInputElement;
    const submitBtn   = form.querySelector('.mwair-lead-submit')  as HTMLButtonElement;
    const dismissBtn  = form.querySelector('.mwair-lead-dismiss') as HTMLButtonElement;

    submitBtn.onclick = async () => {
      const email = emailInput.value.trim();
      if (!email || !email.includes('@')) {
        emailInput.style.borderColor = '#ef4444';
        return;
      }
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sent!';
      await this.api.captureLead(email, question);
      setTimeout(() => form.remove(), 1500);
    };

    dismissBtn.onclick = () => form.remove();

    this.messagesContainer.appendChild(form);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  private addMessage(role: 'user' | 'assistant', content: string, persist = true): void {
    this.messages.push({ role, content, timestamp: new Date() });
    if (persist) this.api.saveMessages(this.messages);

    if (this.messagesContainer) {
      this.renderMessage(role, content);
    }
  }

  private renderMessages(): void {
    if (!this.messagesContainer) return;
    this.messagesContainer.innerHTML = '';
    for (const message of this.messages) {
      this.renderMessage(message.role, message.content);
    }
  }

  private renderMessage(role: 'user' | 'assistant', content: string): void {
    if (!this.messagesContainer) return;

    const msgEl = document.createElement('div');
    msgEl.className = `mwair-message mwair-message-${role}`;
    msgEl.textContent = content;
    this.messagesContainer.appendChild(msgEl);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  private showTyping(): void {
    if (this.messagesContainer) {
      const typingEl = document.createElement('div');
      typingEl.className = 'mwair-typing-indicator';
      typingEl.id = 'mwair-typing';
      typingEl.innerHTML = `
        <div class="mwair-typing-dot"></div>
        <div class="mwair-typing-dot"></div>
        <div class="mwair-typing-dot"></div>
      `;
      this.messagesContainer.appendChild(typingEl);
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
  }

  private hideTyping(): void {
    const typingEl = document.getElementById('mwair-typing');
    if (typingEl) typingEl.remove();
  }

  private getDisplayErrorMessage(error: unknown): string {
    if (error instanceof Error && error.message) {
      const message = error.message;
      if (message === 'Failed to fetch' || message.toLowerCase().includes('network')) {
        return 'I could not reach the chat server. Please check your connection and try again.';
      }
      return message;
    }

    return 'Sorry, something went wrong. Please try again.';
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ─── Public API ───────────────────────────────────

  toggle(): void {
    if (this.isOpen) this.close();
    else this.open();
  }

  open(): void {
    this.isOpen = true;
    this.chatWindow?.classList.add('mwair-open');
    if (this.toggleWrap) this.toggleWrap.style.display = 'none';
  }

  close(): void {
    this.isOpen = false;
    this.chatWindow?.classList.remove('mwair-open');
    if (this.toggleWrap) this.toggleWrap.style.display = 'block';
  }

  show(): void {
    if (this.toggleWrap) this.toggleWrap.style.display = 'block';
    if (this.chatWindow) this.chatWindow.style.display = 'flex';
  }

  hide(): void {
    if (this.toggleWrap) this.toggleWrap.style.display = 'none';
    if (this.chatWindow) this.chatWindow.style.display = 'none';
    this.isOpen = false;
  }

  setOpacity(opacity: number): void {
    const clamped = Math.max(0, Math.min(1, opacity));
    if (this.chatWindow) this.chatWindow.style.opacity = String(clamped);
    if (this.toggleWrap) this.toggleWrap.style.opacity = String(clamped);
  }

  resize(size: 'small' | 'medium' | 'large'): void {
    const sizes = {
      small: { width: '320px', height: '420px' },
      medium: { width: '380px', height: '520px' },
      large: { width: '440px', height: '620px' },
    };
    const s = sizes[size] || sizes.medium;
    if (this.chatWindow) {
      this.chatWindow.style.width = s.width;
      this.chatWindow.style.height = s.height;
    }
  }

  destroy(): void {
    this.toggleWrap?.remove();
    this.chatWindow?.remove();
    const styleEl = document.getElementById('mwair-styles');
    if (styleEl) styleEl.remove();
  }
}
