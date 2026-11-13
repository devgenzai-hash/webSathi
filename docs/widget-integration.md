# Widget Integration Guide

The MakeWebsiteAIReady widget is a self-contained JavaScript bundle that adds an AI chatbot to any website with a single `<script>` tag.

---

## Quick Embed (Simplest Method)

Add this to your website's HTML, just before `</body>`:

```html
<script 
  src="https://your-api-domain.com/widget/chatbot-widget.js"
  data-site-key="YOUR_SITE_KEY"
  data-api-url="https://your-api-domain.com"
></script>
```

That's it. The chatbot icon will appear in the bottom-right corner.

---

## Configuration via Data Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `data-site-key` | string | **(required)** | Your site's unique key (from dashboard) |
| `data-api-url` | string | `window.location.origin` | Backend API base URL |
| `data-position` | string | `bottom-right` | `bottom-right`, `bottom-left`, `top-right`, `top-left` |
| `data-color` | string | `#6366f1` | Primary color (hex) |
| `data-title` | string | `AI Assistant` | Chat window header title |
| `data-welcome-message` | string | `Hello! How can I help you today?` | First message shown |
| `data-opacity` | number | `1` | Widget opacity (0–1) |
| `data-size` | string | `medium` | Window size: `small`, `medium`, `large` |
| `data-hidden` | boolean | `false` | Start hidden (show programmatically) |

### Example with All Options

```html
<script 
  src="https://api.makewebsiteaiready.com/widget/chatbot-widget.js"
  data-site-key="11ea092e-abc1-4def-9012-345678abcdef"
  data-api-url="https://api.makewebsiteaiready.com"
  data-position="bottom-left"
  data-color="#10b981"
  data-title="Support Bot"
  data-welcome-message="Hi! Ask me anything about our products."
  data-size="large"
></script>
```

---

## Programmatic API

After the widget loads, a global `MakeWebsiteAIReady` object is available:

```javascript
// Open the chat window
MakeWebsiteAIReady.open();

// Close the chat window (toggle button remains)
MakeWebsiteAIReady.close();

// Toggle open/close
MakeWebsiteAIReady.toggle();

// Hide completely (chat + toggle button)
MakeWebsiteAIReady.hide();

// Show again after hiding
MakeWebsiteAIReady.show();

// Set opacity (0 to 1)
MakeWebsiteAIReady.setOpacity(0.85);

// Resize the chat window
MakeWebsiteAIReady.resize('small');   // 320×420px
MakeWebsiteAIReady.resize('medium');  // 380×520px (default)
MakeWebsiteAIReady.resize('large');   // 440×620px

// Remove widget completely from the DOM
MakeWebsiteAIReady.destroy();
```

### Conditional Display Example

```html
<script>
// Show chatbot only on specific pages
window.addEventListener('load', () => {
  if (window.location.pathname.startsWith('/docs')) {
    MakeWebsiteAIReady.show();
  } else {
    MakeWebsiteAIReady.hide();
  }
});
</script>
```

---

## JavaScript SDK (NPM)

For frameworks (React, Vue, Angular), install via npm:

```bash
npm install @makewebsiteaiready/chatbot-widget
```

```typescript
import { ChatbotWidget } from '@makewebsiteaiready/chatbot-widget';

const widget = new ChatbotWidget({
  siteKey: 'YOUR_SITE_KEY',
  apiUrl: 'https://api.makewebsiteaiready.com',
  position: 'bottom-right',
  color: '#6366f1',
  title: 'AI Assistant',
  welcomeMessage: 'How can I help?',
  size: 'medium',
});

widget.init();

// Later...
widget.open();
widget.destroy();
```

### TypeScript Types

```typescript
interface WidgetConfig {
  siteKey: string;               // Required
  apiUrl?: string;               // Backend URL
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  color?: string;                // Hex color
  title?: string;                // Header title
  welcomeMessage?: string;       // First message
  opacity?: number;              // 0–1
  size?: 'small' | 'medium' | 'large';
  hidden?: boolean;              // Start hidden
}
```

---

## How It Works

1. **Widget loads** → Fetches configuration from `GET /api/v1/chat/config` (using site key)
2. **User sends message** → `POST /api/v1/chat/` with message, visitor_id, session_id
3. **Backend processes** → RAG retrieval → LLM generation → Response
4. **Widget displays** → Streamed response with typing indicator
5. **Session continuity** → `session_id` is persisted for follow-up context

### Authentication Flow

```
Widget                              Backend
  │                                    │
  ├─── GET /chat/config ──────────────►│  (X-Site-Key header)
  │◄── widget settings ───────────────┤
  │                                    │
  ├─── POST /chat/ ───────────────────►│  (X-Site-Key header)
  │    { message, visitor_id }         │
  │◄── { response, session_id } ──────┤
  │                                    │
  ├─── POST /chat/ ───────────────────►│  (same site key)
  │    { message, visitor_id,          │
  │      session_id }                  │
  │◄── { response, session_id } ──────┤
```

---

## Styling Customization

The widget uses scoped CSS classes prefixed with `mwair-` to avoid conflicts. Override styles with higher specificity:

```css
/* Make the toggle button larger */
.mwair-toggle-btn {
  width: 70px !important;
  height: 70px !important;
}

/* Custom font in chat */
.mwair-chat-messages {
  font-family: 'Inter', sans-serif !important;
}

/* Custom message bubble colors */
.mwair-message-user {
  background-color: #3b82f6 !important;
}
```

---

## Widget Sizes

| Size | Width | Height |
|------|-------|--------|
| `small` | 320px | 420px |
| `medium` | 380px | 520px |
| `large` | 440px | 620px |

---

## Browser Support

- Chrome 80+
- Firefox 78+
- Safari 14+
- Edge 80+
- Mobile browsers (iOS Safari, Chrome Android)

The widget is built as a single IIFE bundle with no external dependencies.
