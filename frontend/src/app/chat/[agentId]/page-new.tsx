"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Agent } from "@/types/agent.types";
import {
  ChatMessage,
  ChatSession,
  StreamingEventType,
} from "@/types/chat.types";
import { AgentService } from "@/services/agent.service";
import { ChatService } from "@/services/chat.service";

// Import new components
import ChatHeader from "@/components/chat/ChatHeader";
import ChatSidebar from "@/components/chat/ChatSidebar";
import ChatMessageContainer from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import EmptyState from "@/components/chat/EmptyState";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params.agentId as string;

  // Core state
  const [agent, setAgent] = useState<Agent | null>(null);
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [conversations, setConversations] = useState<ChatSession[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgent();
    loadAvailableAgents();
  }, [agentId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadAgent = async () => {
    try {
      setError(null);
      const agentData = await AgentService.getAgent(agentId);
      setAgent(agentData);
    } catch (error) {
      console.error("Failed to load agent:", error);
      setError(error instanceof Error ? error.message : "Failed to load agent");
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableAgents = async () => {
    try {
      const agents = await AgentService.getAgents();
      setAvailableAgents(Array.isArray(agents) ? agents : []);
    } catch (error) {
      console.error("Failed to load available agents:", error);
    }
  };

  const startConversation = async (initialMessage: string) => {
    try {
      setIsStreaming(true);
      setError(null);

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        type: "user",
        content: initialMessage,
        timestamp: new Date(),
      };
      setMessages([userMessage]);

      // Start conversation
      const newSession = await ChatService.startConversation(
        agentId,
        initialMessage
      );
      setSession(newSession);

      // Handle streaming response
      let assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "",
        timestamp: new Date(),
      };

      const eventHandler = (event: any) => {
        if (event.type === StreamingEventType.CONTENT) {
          assistantMessage.content += event.content;
          setMessages((prev) => {
            const updated = Array.isArray(prev) ? [...prev] : [];
            const lastIndex = updated.length - 1;
            if (
              updated[lastIndex]?.type === "assistant" &&
              updated[lastIndex]?.id === assistantMessage.id
            ) {
              updated[lastIndex] = { ...assistantMessage };
            } else {
              updated.push({ ...assistantMessage });
            }
            return updated;
          });
        } else if (event.type === StreamingEventType.COMPLETE) {
          setIsStreaming(false);
        } else if (event.type === StreamingEventType.ERROR) {
          console.error("Streaming error:", event.content);
          setError(`Streaming error: ${event.content}`);
          setIsStreaming(false);
        }
      };

      await ChatService.sendMessage(
        newSession.id,
        initialMessage,
        eventHandler
      );
    } catch (error) {
      console.error("Failed to start conversation:", error);
      setError(
        error instanceof Error ? error.message : "Failed to start conversation"
      );
      setIsStreaming(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    if (!session) {
      // Start new conversation
      await startConversation(messageText);
      return;
    }

    if (isStreaming) return;

    setIsStreaming(true);
    setError(null);

    try {
      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        type: "user",
        content: messageText,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Prepare assistant message
      let assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "",
        timestamp: new Date(),
      };

      const eventHandler = (event: any) => {
        if (event.type === StreamingEventType.CONTENT) {
          assistantMessage.content += event.content;
          setMessages((prev) => {
            const updated = Array.isArray(prev) ? [...prev] : [];
            const lastIndex = updated.length - 1;
            if (
              updated[lastIndex]?.type === "assistant" &&
              updated[lastIndex].id === assistantMessage.id
            ) {
              updated[lastIndex] = { ...assistantMessage };
            } else {
              updated.push({ ...assistantMessage });
            }
            return updated;
          });
        } else if (event.type === StreamingEventType.COMPLETE) {
          setIsStreaming(false);
        } else if (event.type === StreamingEventType.ERROR) {
          console.error("Streaming error:", event.content);
          setError(`Streaming error: ${event.content}`);
          setIsStreaming(false);
        }
      };

      await ChatService.sendMessage(session.id, messageText, eventHandler);
    } catch (error) {
      console.error("Failed to send message:", error);
      setError(
        error instanceof Error ? error.message : "Failed to send message"
      );
      setIsStreaming(false);
    }
  };

  const handleAgentSelect = (newAgentId: string) => {
    router.push(`/chat/${newAgentId}`);
    setSidebarOpen(false);
  };

  const handleNewChat = () => {
    setSession(null);
    setMessages([]);
    setSidebarOpen(false);
  };

  const handleExampleClick = (example: string) => {
    sendMessage(example);
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading agent...</p>
        </div>
      </div>
    );
  }

  if (error && !agent) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Error Loading Agent
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push("/agents")}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Go to Agents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <ChatSidebar
        agents={availableAgents}
        conversations={conversations}
        currentAgentId={agentId}
        onAgentSelect={handleAgentSelect}
        onNewChat={handleNewChat}
        onConversationSelect={(id) => console.log("Load conversation:", id)}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <ChatHeader agent={agent} onMenuClick={() => setSidebarOpen(true)} />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <EmptyState
              agentName={agent?.name}
              onExampleClick={handleExampleClick}
            />
          ) : (
            <div className="max-w-4xl mx-auto p-6">
              {messages.map((message) => (
                <ChatMessageContainer key={message.id} message={message} />
              ))}

              {/* Streaming Indicator */}
              {isStreaming && (
                <div className="flex items-center space-x-2 text-gray-400 ml-11">
                  <div className="flex space-x-1">
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                  <span className="text-sm">Thinking...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error Banner */}
        {error && (
          <div className="px-6 py-3 bg-red-50 border-t border-red-200">
            <div className="max-w-4xl mx-auto flex items-center justify-between">
              <p className="text-sm text-red-600">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <ChatInput
          onSend={sendMessage}
          disabled={isStreaming}
          modelName={agent?.name || "AI Assistant"}
        />
      </div>
    </div>
  );
}
