export function getStyles(color: string, position: string): string {
  const positionStyles: Record<string, string> = {
    'bottom-right': 'bottom: 20px; right: 20px;',
    'bottom-left': 'bottom: 20px; left: 20px;',
    'top-right': 'top: 20px; right: 20px;',
    'top-left': 'top: 20px; left: 20px;',
  };

  const btnPosition: Record<string, string> = {
    'bottom-right': 'bottom: 20px; right: 20px;',
    'bottom-left': 'bottom: 20px; left: 20px;',
    'top-right': 'top: 20px; right: 20px;',
    'top-left': 'top: 20px; left: 20px;',
  };

  return `
    .mwair-widget-container {
      position: fixed;
      ${positionStyles[position] || positionStyles['bottom-right']}
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }

    .mwair-toggle-wrap {
      position: fixed;
      ${btnPosition[position] || btnPosition['bottom-right']}
      z-index: 999999;
      width: 64px;
      height: 64px;
    }

    .mwair-toggle-btn {
      position: absolute;
      right: 0;
      bottom: 0;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: ${color};
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .mwair-hide-widget-btn {
      position: absolute;
      top: 0;
      right: 0;
      z-index: 1000000;
      width: 18px;
      height: 18px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.85);
      background: #111827;
      color: white;
      cursor: pointer;
      font-size: 14px;
      line-height: 15px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.22);
      opacity: 0.9;
      transition: opacity 0.2s, transform 0.2s;
    }

    .mwair-hide-widget-btn:hover {
      opacity: 1;
      transform: scale(1.08);
    }

    .mwair-toggle-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }

    .mwair-toggle-btn svg {
      width: 28px;
      height: 28px;
      fill: white;
    }

    .mwair-chat-window {
      position: fixed;
      ${positionStyles[position] || positionStyles['bottom-right']}
      width: 380px;
      height: 520px;
      max-height: 80vh;
      max-width: 90vw;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(20px) scale(0.95);
      transition: opacity 0.3s, transform 0.3s;
      pointer-events: none;
    }

    .mwair-chat-window.mwair-open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: all;
    }

    .mwair-chat-header {
      background: ${color};
      color: white;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }

    .mwair-chat-header h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .mwair-header-actions {
      display: flex;
      gap: 8px;
    }

    .mwair-header-btn {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      opacity: 0.8;
      transition: opacity 0.2s;
    }

    .mwair-header-btn:hover {
      opacity: 1;
    }

    .mwair-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .mwair-message {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 12px;
      word-wrap: break-word;
      animation: mwair-fadeIn 0.3s ease;
    }

    @keyframes mwair-fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .mwair-message-user {
      align-self: flex-end;
      background: ${color};
      color: white;
      border-bottom-right-radius: 4px;
    }

    .mwair-message-assistant {
      align-self: flex-start;
      background: #f1f3f5;
      color: #1a1a1a;
      border-bottom-left-radius: 4px;
    }

    .mwair-typing-indicator {
      align-self: flex-start;
      background: #f1f3f5;
      padding: 12px 16px;
      border-radius: 12px;
      display: flex;
      gap: 4px;
    }

    .mwair-typing-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #999;
      animation: mwair-bounce 1.4s infinite both;
    }

    .mwair-typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .mwair-typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes mwair-bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-6px); }
    }

    .mwair-chat-input {
      display: flex;
      padding: 12px 16px;
      border-top: 1px solid #e9ecef;
      gap: 8px;
      flex-shrink: 0;
    }

    .mwair-chat-input input {
      flex: 1;
      border: 1px solid #dee2e6;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }

    .mwair-chat-input input:focus {
      border-color: ${color};
    }

    .mwair-chat-input button {
      background: ${color};
      color: white;
      border: none;
      border-radius: 8px;
      padding: 10px 16px;
      cursor: pointer;
      font-weight: 500;
      transition: opacity 0.2s;
    }

    .mwair-chat-input button:hover {
      opacity: 0.9;
    }

    .mwair-chat-input button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .mwair-powered-by {
      text-align: center;
      padding: 6px;
      font-size: 11px;
      color: #999;
      border-top: 1px solid #f1f3f5;
    }

    .mwair-powered-by a {
      color: #666;
      text-decoration: none;
    }

    /* Lead-capture form */
    .mwair-lead-capture {
      margin: 8px 12px;
      padding: 12px;
      background: #f0f9ff;
      border: 1px solid #bae6fd;
      border-radius: 10px;
    }

    .mwair-lead-title {
      font-weight: 600;
      font-size: 13px;
      margin: 0 0 2px;
      color: #0369a1;
    }

    .mwair-lead-sub {
      font-size: 12px;
      color: #64748b;
      margin: 0 0 8px;
    }

    .mwair-lead-email {
      width: 100%;
      box-sizing: border-box;
      padding: 6px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 13px;
      outline: none;
      margin-bottom: 8px;
    }

    .mwair-lead-email:focus { border-color: ${color}; }

    .mwair-lead-actions { display: flex; gap: 6px; }

    .mwair-lead-submit {
      flex: 1;
      padding: 6px;
      background: ${color};
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
    }

    .mwair-lead-submit:disabled { opacity: 0.6; cursor: default; }

    .mwair-lead-dismiss {
      padding: 6px 10px;
      background: transparent;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      color: #64748b;
    }
  `;
}
