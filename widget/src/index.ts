import { ChatbotWidget } from './chatbot';
import { WidgetConfig } from './types';

export { ChatbotWidget } from './chatbot';
export type { WidgetConfig, ChatMessage } from './types';

/**
 * Auto-initialize from script tag attributes.
 * Usage:
 *   <script src="chatbot-widget.js" data-site-key="YOUR_KEY"></script>
 */
function autoInit(): void {
  // Find the script tag
  const scripts = document.querySelectorAll('script[data-site-key]');
  const script = scripts[scripts.length - 1] as HTMLScriptElement | undefined;

  if (!script) return;

  const config: WidgetConfig = {
    siteKey: script.getAttribute('data-site-key') || '',
    apiUrl: script.getAttribute('data-api-url') || undefined,
    position: (script.getAttribute('data-position') as any) || 'bottom-right',
    color: script.getAttribute('data-color') || undefined,
    title: script.getAttribute('data-title') || undefined,
    welcomeMessage: script.getAttribute('data-welcome-message') || undefined,
    opacity: script.getAttribute('data-opacity') ? parseFloat(script.getAttribute('data-opacity')!) : undefined,
    size: (script.getAttribute('data-size') as any) || undefined,
    hidden: script.getAttribute('data-hidden') === 'true',
  };

  if (!config.siteKey) {
    console.error('[MakeWebsiteAIReady] Missing data-site-key attribute');
    return;
  }

  const widget = new ChatbotWidget(config);
  widget.init();

  // Expose globally for programmatic control
  (window as any).MakeWebsiteAIReady = {
    widget,
    open: () => widget.open(),
    close: () => widget.close(),
    toggle: () => widget.toggle(),
    hide: () => widget.hide(),
    show: () => widget.show(),
    setOpacity: (o: number) => widget.setOpacity(o),
    resize: (s: 'small' | 'medium' | 'large') => widget.resize(s),
    destroy: () => widget.destroy(),
  };
}

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoInit);
} else {
  autoInit();
}
