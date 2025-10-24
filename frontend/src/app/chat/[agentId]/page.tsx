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

// Import components
import ChatHeader from "@/components/chat/ChatHeader";
import ChatSidebar from "@/components/chat/ChatSidebar";
import ChatMessageContainer from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import EmptyState from "@/components/chat/EmptyState";
import ChatDrawer from "@/components/chat/ChatDrawer";
import { FaPause } from "react-icons/fa";

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
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [conversations, setConversations] = useState<ChatSession[]>([]);

  // Tool & Configuration state
  const [availableTools, setAvailableTools] = useState<string[]>([]);
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const [isReactMode, setIsReactMode] = useState(false);
  const [plannerEnabled, setPlannerEnabled] = useState(false);
  const [facebookConnected, setFacebookConnected] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgent();
    loadAvailableAgents();
    loadAvailableTools();
    loadConversations();
  }, [agentId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (agent) {
      setActiveTools(agent.tools || []);
      setIsReactMode(agent.agent_type === "react");
      setPlannerEnabled(!!agent.planner);
    }
  }, [agent]);

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

  const loadAvailableTools = async () => {
    try {
      const tools = await AgentService.getAvailableTools();
      setAvailableTools(Array.isArray(tools) ? tools : []);
    } catch (error) {
      console.error("Failed to load available tools:", error);
    }
  };

  const loadConversations = async () => {
    try {
      const convs = await ChatService.getConversations(agentId);
      setConversations(convs);
      console.log("Loaded conversations:", convs);
    } catch (error) {
      console.error("Failed to load conversations:", error);
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
        } else if (event.content && event.content.trim()) {
          // Handle other event types (tool calls, tool responses, etc.)
          const eventMessage: ChatMessage = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: "system",
            content: event.content.trim(),
            timestamp: new Date(),
            eventType: event.type,
            metadata: event.metadata,
          };
          setMessages((prev) => {
            const updated = Array.isArray(prev) ? [...prev] : [];
            return [...updated, eventMessage];
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
      
      // Reload conversations list
      await loadConversations();
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
        } else if (event.content && event.content.trim()) {
          // Handle other event types
          const eventMessage: ChatMessage = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: "system",
            content: event.content.trim(),
            timestamp: new Date(),
            eventType: event.type,
            metadata: event.metadata,
          };
          setMessages((prev) => {
            const updated = Array.isArray(prev) ? [...prev] : [];
            return [...updated, eventMessage];
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

  const handleConversationSelect = async (conversationId: string) => {
    try {
      // Load conversation from API
      const conversation = await ChatService.getConversation(conversationId);

      // Set session
      setSession({
        id: conversation.session_id,
        agent_id: conversation.agent_id,
        user_id: conversation.user_id,
        created_at: conversation.created_at,
        updated_at: conversation.updated_at,
        is_active: conversation.is_active,
        messages: [],
      });

      // Transform and set messages
      const transformedMessages = conversation.messages.map((msg: any) => ({
        id: msg.message_id || `${Date.now()}-${Math.random()}`,
        type: msg.role === "user" ? "user" : msg.role === "assistant" ? "assistant" : "system",
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        metadata: msg.metadata,
      }));

      setMessages(transformedMessages);

      // Close sidebar
      setSidebarOpen(false);
    } catch (error) {
      console.error("Failed to load conversation:", error);
      setError("Failed to load conversation");
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await ChatService.deleteConversation(conversationId);
      
      // If deleting current conversation, start new chat
      if (session?.id === conversationId) {
        handleNewChat();
      }
      
      // Reload conversations list
      await loadConversations();
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      setError("Failed to delete conversation");
    }
  };

  const handleExampleClick = (example: string) => {
    sendMessage(example);
  };

  const toggleTool = async (toolName: string) => {
    if (!agent) return;

    try {
      const isActive = activeTools.includes(toolName);

      if (isActive) {
        await AgentService.detachTools(agent.id, [toolName]);
        setActiveTools((prev) => prev.filter((t) => t !== toolName));
      } else {
        await AgentService.attachTools(agent.id, [toolName]);
        setActiveTools((prev) => [...prev, toolName]);
      }

      await loadAgent();
    } catch (error) {
      console.error("Failed to toggle tool:", error);
      setError(
        error instanceof Error ? error.message : "Failed to update tool"
      );
    }
  };

  const updateAgentConfig = async (config: {
    agent_type?: string;
    planner?: string;
  }) => {
    if (!agent) return;

    try {
      await AgentService.updateAgentConfig(agent.id, config);
      await loadAgent();
    } catch (error) {
      console.error("Failed to update agent config:", error);
      setError(
        error instanceof Error ? error.message : "Failed to update agent"
      );
    }
  };

  const toggleReactMode = async () => {
    if (!agent) return;
    
    try {
      // Optimistically update UI
      const newReactMode = !isReactMode;
      setIsReactMode(newReactMode);
      setPlannerEnabled(newReactMode);
      
      // When enabling ReAct mode, use PlanReActPlanner
      // When disabling, remove both agent_type and planner
      const newMode = newReactMode ? "react" : undefined;
      await updateAgentConfig({
        agent_type: newMode,
        planner: newMode === "react" ? "PlanReActPlanner" : undefined,
      });
      
      console.log(`✅ ReAct mode ${newReactMode ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
      // Revert on error
      console.error("Failed to toggle ReAct mode:", error);
      setIsReactMode(!isReactMode);
      setPlannerEnabled(!plannerEnabled);
      setError("Failed to toggle ReAct mode");
    }
  };

  const togglePlanner = async () => {
    // This is now handled by toggleReactMode
    // Keep for backward compatibility but it does the same as toggleReactMode
    await toggleReactMode();
  };

  const stopStreaming = async () => {
    if (agent && isStreaming) {
      try {
        await AgentService.stopStreaming(agent.id);
        setIsStreaming(false);
      } catch (error) {
        console.error("Failed to stop streaming:", error);
        setError("Failed to stop streaming");
      }
    }
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
        onConversationSelect={handleConversationSelect}
        onDeleteConversation={handleDeleteConversation}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <ChatHeader
          agent={agent}
          availableAgents={availableAgents}
          onMenuClick={() => setSidebarOpen(true)}
          onSettingsClick={() => setDrawerOpen(true)}
          onAgentSelect={handleAgentSelect}
          isReactMode={isReactMode}
          plannerEnabled={plannerEnabled}
          activeToolsCount={activeTools.length}
          facebookConnected={facebookConnected}
        />

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
                <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <div className="flex space-x-1">
                      <div
                        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">Thinking...</span>
                  </div>
                  <button
                    onClick={stopStreaming}
                    className="flex items-center space-x-1 px-3 py-1 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors"
                  >
                    <FaPause />
                    <span>Stop</span>
                  </button>
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

      {/* Settings Drawer */}
      <ChatDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        agent={agent}
        availableTools={availableTools}
        activeTools={activeTools}
        onToggleTool={toggleTool}
        isReactMode={isReactMode}
        plannerEnabled={plannerEnabled}
        onToggleReactMode={toggleReactMode}
        onTogglePlanner={togglePlanner}
        agentId={agentId}
        sessionId={session?.id}
        onFacebookConnectionChange={setFacebookConnected}
      />
    </div>
  );
}
