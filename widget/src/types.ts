export interface WidgetConfig {
  siteKey: string;
  apiUrl?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  color?: string;
  title?: string;
  welcomeMessage?: string;
  opacity?: number;
  size?: 'small' | 'medium' | 'large';
  hidden?: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources: string[];
  confidence?: 'high' | 'medium' | 'low';
  was_answered?: boolean;
}

export interface ChatHistoryResponse {
  session_id: string | null;
  messages: ChatHistoryMessage[];
}

export interface ChatHistoryMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
  timestamp?: string;
}

export interface WidgetConfigResponse {
  widget_position: string;
  widget_color: string;
  widget_title: string;
  widget_welcome_message: string;
  hide_branding?: boolean;
}
