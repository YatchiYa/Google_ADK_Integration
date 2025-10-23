export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  eventType?: StreamingEventType;
  metadata?: Record<string, any>;
}

export interface StreamingEvent {
  type: StreamingEventType;
  content: string;
  metadata?: Record<string, any>;
  timestamp: number;
  session_id: string;
  message_id?: string;
}

export enum StreamingEventType {
  START = 'start',
  CONTENT = 'content',
  TOOL_CALL = 'tool_call',
  TOOL_RESPONSE = 'tool_response',
  TOOL_RESULT = 'tool_result',
  THINKING = 'thinking',
  ERROR = 'error',
  COMPLETE = 'complete',
  METADATA = 'metadata'
}

export interface ChatSession {
  id: string;
  agent_id: string;
  user_id: string;
  created_at: string;
  last_activity: string;
  is_active: boolean;
  message_count: number;
}

export interface StartConversationRequest {
  user_id: string;
  agent_id: string;
  message: string;
  context?: Record<string, any>;
}

export interface SendMessageRequest {
  message: string;
  stream?: boolean;
  context?: Record<string, any>;
}
