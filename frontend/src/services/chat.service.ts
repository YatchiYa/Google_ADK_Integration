import { AuthService } from './auth.service';
import { 
  ChatSession, 
  StartConversationRequest, 
  SendMessageRequest, 
  StreamingEvent,
  StreamingEventType 
} from '@/types/chat.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ChatServiceClass {
  async startConversation(agentId: string, initialMessage: string): Promise<ChatSession> {
    const userId = AuthService.getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const request: StartConversationRequest = {
      user_id: userId,
      agent_id: agentId,
      message: initialMessage,
      context: {
        frontend_client: true,
        session_type: 'interactive'
      }
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/start`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start conversation');
    }

    const result = await response.json();
    
    // Extract session ID from message
    const sessionIdMatch = result.message.match(/session_([a-f0-9]+)/);
    if (!sessionIdMatch) {
      throw new Error('Failed to extract session ID from response');
    }

    return {
      id: sessionIdMatch[0],
      agent_id: agentId,
      user_id: userId,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      is_active: true,
      message_count: 1
    };
  }

  async sendMessage(
    sessionId: string, 
    message: string, 
    onEvent?: (event: StreamingEvent) => void
  ): Promise<void> {
    const request: SendMessageRequest = {
      message,
      stream: true,
      context: {
        frontend_client: true
      }
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/streaming/send?session_id=${sessionId}`, {
      method: 'POST',
      headers: {
        ...AuthService.getAuthHeaders(),
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const eventData = line.slice(6);
            
            if (eventData === '[DONE]') {
              return;
            }

            try {
              const event: StreamingEvent = JSON.parse(eventData);
              onEvent?.(event);
            } catch (error) {
              console.error('Failed to parse streaming event:', error);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getConversationHistory(sessionId: string): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${sessionId}/history`, {
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch conversation history');
    }

    const data = await response.json();
    return data.messages || [];
  }

  async getConversations(agentId: string): Promise<ChatSession[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/conversations/agent/${agentId}`,
        {
          headers: AuthService.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load conversations");
      }

      const data = await response.json();

      // Transform to ChatSession format
      return (data.conversations || []).map((conv: any) => ({
        id: conv.session_id,
        agent_id: conv.agent_id,
        user_id: conv.user_id,
        created_at: conv.created_at,
        updated_at: conv.updated_at,
        is_active: conv.is_active,
        messages: conv.messages || [],
      }));
    } catch (error) {
      console.error("Error loading conversations:", error);
      return [];
    }
  }

  async getConversation(conversationId: string): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/conversations/${conversationId}`,
        {
          headers: AuthService.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load conversation");
      }

      return await response.json();
    } catch (error) {
      console.error("Error loading conversation:", error);
      throw error;
    }
  }

  async endConversation(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${sessionId}/end`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to end conversation');
    }
  }

  // Utility method to create a streaming event handler
  createEventHandler(
    onContent: (content: string, eventType: StreamingEventType) => void,
    onToolCall?: (toolName: string, args: any) => void,
    onToolResponse?: (toolName: string, response: any) => void,
    onError?: (error: string) => void,
    onComplete?: () => void
  ) {
    return (event: StreamingEvent) => {
      switch (event.type) {
        case StreamingEventType.CONTENT:
          onContent(event.content, event.type);
          break;
          
        case StreamingEventType.TOOL_CALL:
          if (onToolCall && event.metadata) {
            onToolCall(event.metadata.tool_name, event.metadata.tool_args);
          }
          onContent(event.content, event.type);
          break;
          
        case StreamingEventType.TOOL_RESPONSE:
          if (onToolResponse && event.metadata) {
            onToolResponse(event.metadata.tool_name, event.metadata.response);
          }
          onContent(event.content, event.type);
          break;
          
        case StreamingEventType.THINKING:
          onContent(event.content, event.type);
          break;
          
        case StreamingEventType.ERROR:
          if (onError) {
            onError(event.content);
          } else {
            onContent(`Error: ${event.content}`, event.type);
          }
          break;
          
        case StreamingEventType.COMPLETE:
          onComplete?.();
          break;
          
        default:
          // Handle other event types
          if (event.content) {
            onContent(event.content, event.type);
          }
      }
    };
  }

  async deleteConversation(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${sessionId}`, {
      method: 'DELETE',
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete conversation');
    }
  }
}

export const ChatService = new ChatServiceClass();
