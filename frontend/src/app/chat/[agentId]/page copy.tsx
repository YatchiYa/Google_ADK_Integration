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
import AuthenticatedImage from "@/components/AuthenticatedImage";
import FacebookConnectionPanel from "@/components/FacebookConnectionPanel";
import {
  FaRobot,
  FaUser,
  FaPaperPlane,
  FaArrowLeft,
  FaCog,
  FaCheck,
  FaBrain,
  FaComment,
  FaSpinner,
  FaTools,
  FaExchangeAlt,
  FaPlay,
  FaPause,
  FaToggleOn,
  FaToggleOff,
  FaWrench,
  FaChevronDown,
  FaChevronUp,
  FaEllipsisV,
  FaCopy,
  FaThumbsUp,
  FaThumbsDown,
  FaFacebook,
} from "react-icons/fa";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const agentId = params.agentId as string;

  const [agent, setAgent] = useState<Agent | null>(null);
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enhanced chat features
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [availableTools, setAvailableTools] = useState<string[]>([]);
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const [showToolPanel, setShowToolPanel] = useState(false);
  const [showAgentPanel, setShowAgentPanel] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isReactMode, setIsReactMode] = useState(false);
  const [plannerEnabled, setPlannerEnabled] = useState(false);
  const [facebookConnected, setFacebookConnected] = useState(false);

  // Interactive features
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(
    new Set()
  );
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [showToolDetails, setShowToolDetails] = useState<Set<string>>(
    new Set()
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgent();
    loadAvailableAgents();
    loadAvailableTools();
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

  const loadAgent = async () => {
    try {
      setError(null);
      const agentData = await AgentService.getAgent(agentId);
      console.log("Loaded agent for chat:", agentData); // Debug log
      setAgent(agentData);
    } catch (error) {
      console.error("Failed to load agent:", error);
      setError(error instanceof Error ? error.message : "Failed to load agent");
      // Don't automatically redirect, let user see the error
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
        console.log("Raw streaming event:", event);

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
          // Handle other event types (tool calls, tool responses, etc.) with full metadata
          const eventMessage: ChatMessage = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: "system",
            content: event.content.trim(),
            timestamp: new Date(),
            eventType: event.type,
            metadata: event.metadata, // Preserve the full metadata!
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

  const sendMessage = async () => {
    if (!newMessage.trim() || !session || isStreaming) return;

    const messageText = newMessage.trim();
    setNewMessage("");
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
        console.log("Raw streaming event:", event);

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
          // Handle other event types (tool calls, tool responses, etc.) with full metadata
          const eventMessage: ChatMessage = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: "system",
            content: event.content.trim(),
            timestamp: new Date(),
            eventType: event.type,
            metadata: event.metadata, // Preserve the full metadata!
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
          const errorMessage: ChatMessage = {
            id: Date.now().toString(),
            type: "system",
            content: `Error: ${event.content}`,
            timestamp: new Date(),
            eventType: StreamingEventType.ERROR,
          };
          setMessages((prev) => [...prev, errorMessage]);
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

  // Tool Management Functions
  const toggleTool = async (toolName: string) => {
    if (!agent) return;

    try {
      const isActive = activeTools.includes(toolName);

      if (isActive) {
        // Detach tool
        await AgentService.detachTools(agent.id, [toolName]);
        setActiveTools((prev) => prev.filter((t) => t !== toolName));
      } else {
        // Attach tool
        await AgentService.attachTools(agent.id, [toolName]);
        setActiveTools((prev) => [...prev, toolName]);
      }

      // Update agent data
      await loadAgent();
    } catch (error) {
      console.error("Failed to toggle tool:", error);
      setError(
        error instanceof Error ? error.message : "Failed to update tool"
      );
    }
  };

  // Agent Configuration Functions
  const updateAgentConfig = async (config: {
    agent_type?: string;
    planner?: string;
    tools?: string[];
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
    const newMode = isReactMode ? undefined : "react";
    await updateAgentConfig({
      agent_type: newMode,
      planner: newMode === "react" ? "default" : undefined,
    });
  };

  const togglePlanner = async () => {
    const newPlanner = plannerEnabled ? undefined : "default";
    await updateAgentConfig({ planner: newPlanner });
  };

  // Interactive Functions
  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      console.error("Failed to copy text:", error);
    }
  };

  const toggleMessageExpansion = (messageId: string) => {
    setExpandedMessages((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  const toggleToolDetails = (messageId: string) => {
    setShowToolDetails((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
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

  // Agent Switching
  const switchAgent = (newAgentId: string) => {
    if (newAgentId !== agentId) {
      router.push(`/chat/${newAgentId}`);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const getEventIcon = (eventType?: StreamingEventType) => {
    switch (eventType) {
      case StreamingEventType.TOOL_CALL:
        return <FaWrench className="text-blue-500 animate-spin" />;
      case StreamingEventType.TOOL_RESPONSE:
        return <FaCheck className="text-green-500" />;
      case StreamingEventType.THINKING:
        return <FaBrain className="text-purple-500 animate-pulse" />;
      case StreamingEventType.ERROR:
        return <span className="text-red-500 text-lg">⚠️</span>;
      default:
        return <FaComment className="text-gray-500" />;
    }
  };

  const renderToolCallMessage = (message: ChatMessage) => {
    const showDetails = showToolDetails.has(message.id);

    if (message.eventType === StreamingEventType.TOOL_CALL) {
      // Parse metadata if available
      let toolName = "Unknown Tool";
      let toolArgs = {};
      let callId = "";

      try {
        // Try to extract tool info from content or metadata
        if (message.metadata) {
          toolName = message.metadata.tool_name || toolName;
          toolArgs = message.metadata.tool_args || {};
          callId = message.metadata.call_id || "";
        } else {
          // Parse from content if metadata not available
          const match = message.content.match(/Calling tool: (\w+)/);
          if (match) toolName = match[1];
        }
      } catch (error) {
        console.error("Error parsing tool call metadata:", error);
      }

      return (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <FaWrench className="text-blue-500 animate-spin" />
              <span className="font-medium text-blue-800">Tool Call</span>
              <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full">
                {toolName}
              </span>
            </div>
            <button
              onClick={() => toggleToolDetails(message.id)}
              className="text-blue-600 hover:text-blue-800 text-xs"
            >
              {showDetails ? <FaChevronUp /> : <FaChevronDown />}
            </button>
          </div>

          <div className="text-sm text-blue-700 bg-blue-100 p-2 rounded mb-2">
            {message.content}
          </div>

          {showDetails && (
            <div className="mt-3 space-y-2">
              {Object.keys(toolArgs).length > 0 && (
                <div>
                  <div className="text-xs font-medium text-blue-800 mb-1">
                    Arguments:
                  </div>
                  <div className="text-xs bg-blue-200 p-2 rounded font-mono">
                    {JSON.stringify(toolArgs, null, 2)}
                  </div>
                </div>
              )}
              {callId && (
                <div>
                  <div className="text-xs font-medium text-blue-800 mb-1">
                    Call ID:
                  </div>
                  <div className="text-xs text-blue-600 font-mono">
                    {callId}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    if (message.eventType === StreamingEventType.TOOL_RESPONSE) {
      let toolName = "Unknown Tool";
      let toolResult = null;
      let rawResponse = null;

      try {
        if (message.metadata) {
          toolName = message.metadata.tool_name || toolName;
          toolResult = message.metadata.tool_result;
          rawResponse = message.metadata.raw_response;
        }
      } catch (error) {
        console.error("Error parsing tool response metadata:", error);
      }

      // Check if this is an image generation tool
      const isImageTool =
        toolName.includes("image") ||
        toolName.includes("gemini_text_to_image") ||
        toolName.includes("gemini_image");
      const hasImageResult =
        toolResult && (toolResult.main_image_path || toolResult.main_image_url);

      // Debug logging
      console.log("Tool Response Debug:", {
        toolName,
        isImageTool,
        hasImageResult,
        toolResult,
        main_image_url: toolResult?.main_image_url,
        main_image_filename: toolResult?.main_image_filename,
      });

      // Additional debug for image rendering
      if (hasImageResult) {
        console.log("Will render image section for:", toolName);
        const imageUrl = toolResult.main_image_url?.startsWith("http")
          ? toolResult.main_image_url
          : `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${
              toolResult.main_image_url ||
              `/api/v1/images/serve/${
                toolResult.main_image_filename ||
                toolResult.main_image_path?.split("/").pop()
              }`
            }`;
        console.log("Image URL will be:", imageUrl);
      }

      return (
        <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <FaCheck className="text-green-500" />
              <span className="font-medium text-green-800">Tool Response</span>
              <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">
                {toolName}
              </span>
              {toolResult && toolResult.success && (
                <span className="text-xs bg-green-300 text-green-900 px-2 py-1 rounded-full">
                  Success
                </span>
              )}
            </div>
            <button
              onClick={() => toggleToolDetails(message.id)}
              className="text-green-600 hover:text-green-800 text-xs"
            >
              {showDetails ? <FaChevronUp /> : <FaChevronDown />}
            </button>
          </div>

          <div className="text-sm text-green-700 bg-green-100 p-2 rounded mb-2">
            {showDetails
              ? message.content
              : message.content.length > 200
              ? `${message.content.substring(0, 200)}...`
              : message.content}
          </div>

          {/* Tool Summary Info */}
          {toolResult && (
            <div className="bg-white p-3 rounded-lg border mb-2">
              <div className="text-xs font-medium text-green-800 mb-2">
                Tool Summary:
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                {toolResult.success !== undefined && (
                  <div>
                    <strong>Status:</strong>{" "}
                    {toolResult.success ? "✅ Success" : "❌ Failed"}
                  </div>
                )}
                {toolResult.prompt && (
                  <div>
                    <strong>Prompt:</strong> {toolResult.prompt}
                  </div>
                )}
                {toolResult.model_used && (
                  <div>
                    <strong>Model:</strong> {toolResult.model_used}
                  </div>
                )}
                {toolResult.generation_type && (
                  <div>
                    <strong>Type:</strong> {toolResult.generation_type}
                  </div>
                )}
                {toolResult.total_images && (
                  <div>
                    <strong>Images Generated:</strong> {toolResult.total_images}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Always Show Generated Images */}
          {hasImageResult && (
            <div className="mt-3 mb-3">
              <div className="bg-white p-3 rounded-lg border">
                <div className="text-xs font-medium text-green-800 mb-2">
                  Generated Image:
                </div>
                <div className="space-y-2">
                  <AuthenticatedImage
                    src={
                      toolResult.main_image_url?.startsWith("http")
                        ? toolResult.main_image_url
                        : `${
                            process.env.NEXT_PUBLIC_API_URL ||
                            "http://localhost:8000"
                          }${
                            toolResult.main_image_url ||
                            `/api/v1/images/serve/${
                              toolResult.main_image_filename ||
                              toolResult.main_image_path?.split("/").pop()
                            }`
                          }`
                    }
                    alt={toolResult.prompt || "Generated image"}
                    className="max-w-full h-auto rounded-lg shadow-sm border"
                    style={{ maxHeight: "400px" }}
                    onError={(e) => {
                      console.error("Failed to load image:", e);
                      console.error("Tool result:", toolResult);
                    }}
                    onLoad={() => {
                      console.log("Image loaded successfully!");
                    }}
                  />
                  <div className="text-xs text-gray-600">
                    <div>
                      <strong>Prompt:</strong> {toolResult.prompt}
                    </div>
                    <div>
                      <strong>Model:</strong> {toolResult.model_used}
                    </div>
                    <div>
                      <strong>Type:</strong> {toolResult.generation_type}
                    </div>
                    {toolResult.total_images > 1 && (
                      <div>
                        <strong>Images Generated:</strong>{" "}
                        {toolResult.total_images}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Expandable Tool Details */}
          {showDetails && toolResult && (
            <div className="mt-3 space-y-3">
              {/* Tool Result Details */}
              <div className="bg-white p-3 rounded-lg border">
                <div className="text-xs font-medium text-green-800 mb-2">
                  Tool Result:
                </div>
                <div className="text-xs bg-gray-100 p-2 rounded font-mono max-h-40 overflow-y-auto">
                  {JSON.stringify(toolResult, null, 2)}
                </div>
              </div>

              {/* Raw Response (if different from tool result) */}
              {rawResponse && rawResponse !== toolResult && (
                <div className="bg-white p-3 rounded-lg border">
                  <div className="text-xs font-medium text-green-800 mb-2">
                    Raw Response:
                  </div>
                  <div className="text-xs bg-gray-100 p-2 rounded font-mono max-h-40 overflow-y-auto">
                    {JSON.stringify(rawResponse, null, 2)}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    if (message.eventType === StreamingEventType.THINKING) {
      return (
        <div className="bg-purple-50 border-l-4 border-purple-400 p-4 rounded-r-lg">
          <div className="flex items-center space-x-2 mb-2">
            <FaBrain className="text-purple-500 animate-pulse" />
            <span className="font-medium text-purple-800">Thinking</span>
          </div>
          <div className="text-sm text-purple-700 italic">
            {message.content}
          </div>
        </div>
      );
    }

    return null;
  };

  const getEventBadgeColor = (eventType?: StreamingEventType) => {
    switch (eventType) {
      case StreamingEventType.TOOL_CALL:
        return "bg-blue-100 text-blue-800";
      case StreamingEventType.TOOL_RESPONSE:
        return "bg-green-100 text-green-800";
      case StreamingEventType.THINKING:
        return "bg-purple-100 text-purple-800";
      case StreamingEventType.ERROR:
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!agent && !loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {error || "Agent Not Found"}
          </h1>
          {error && <p className="text-red-600 mb-4">{error}</p>}
          <div className="space-x-4">
            <button
              onClick={loadAgent}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Try Again
            </button>
            <button
              onClick={() => router.push("/")}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.push("/")}
              className="text-gray-600 hover:text-gray-800 transition-colors"
            >
              <FaArrowLeft className="text-lg" />
            </button>
            <h2 className="font-semibold text-gray-800">Chat Controls</h2>
          </div>

          {/* Agent Selector */}
          <div className="relative">
            <button
              onClick={() => setShowAgentPanel(!showAgentPanel)}
              className="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <FaRobot className="text-white text-sm" />
                </div>
                <div className="text-left">
                  <div className="font-medium text-gray-900 truncate">
                    {agent?.name || "Loading..."}
                  </div>
                  <div className="text-xs text-gray-500">
                    {session
                      ? `Session: ${session.id.slice(-8)}`
                      : "No session"}
                  </div>
                </div>
              </div>
              {showAgentPanel ? <FaChevronUp /> : <FaChevronDown />}
            </button>

            {/* Agent Dropdown */}
            {showAgentPanel && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                {availableAgents.map((availableAgent) => (
                  <button
                    key={availableAgent.id}
                    onClick={() => {
                      switchAgent(availableAgent.id);
                      setShowAgentPanel(false);
                    }}
                    className={`w-full flex items-center space-x-3 p-3 hover:bg-gray-50 transition-colors ${
                      availableAgent.id === agent?.id
                        ? "bg-blue-50 border-l-4 border-blue-500"
                        : ""
                    }`}
                  >
                    <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                      <FaRobot className="text-white text-xs" />
                    </div>
                    <div className="text-left flex-1">
                      <div className="font-medium text-gray-900 text-sm truncate">
                        {availableAgent.name}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {availableAgent.persona?.description}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Agent Configuration */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-800">Agent Configuration</h3>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="text-gray-500 hover:text-gray-700"
            >
              <FaCog />
            </button>
          </div>

          {showSettings && (
            <div className="space-y-3">
              {/* ReAct Mode Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">ReAct Mode</span>
                <button
                  onClick={toggleReactMode}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    isReactMode ? "bg-blue-600" : "bg-gray-200"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      isReactMode ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              {/* Planner Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Planner</span>
                <button
                  onClick={togglePlanner}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    plannerEnabled ? "bg-green-600" : "bg-gray-200"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      plannerEnabled ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Tools Panel */}
        <div className="flex-1 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-800">Tools</h3>
            <button
              onClick={() => setShowToolPanel(!showToolPanel)}
              className="text-gray-500 hover:text-gray-700"
            >
              <FaTools />
            </button>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {availableTools.map((tool) => {
              const isActive = activeTools.includes(tool);
              return (
                <div
                  key={tool}
                  className={`flex items-center justify-between p-2 rounded-lg border transition-colors ${
                    isActive
                      ? "bg-green-50 border-green-200"
                      : "bg-white border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-sm text-gray-700 truncate flex-1">
                    {tool
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                  <button
                    onClick={() => toggleTool(tool)}
                    className={`ml-2 p-1 rounded transition-colors ${
                      isActive
                        ? "text-green-600 hover:text-green-800"
                        : "text-gray-400 hover:text-gray-600"
                    }`}
                  >
                    {isActive ? <FaToggleOn /> : <FaToggleOff />}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Facebook Connection Panel */}
        <div className="p-4 border-t border-gray-200">
          <FacebookConnectionPanel
            agentId={agentId}
            sessionId={session?.id}
            onConnectionChange={setFacebookConnected}
            className="w-full"
          />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <FaRobot className="text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-gray-900">{agent?.name}</h1>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>
                    {session
                      ? `Session: ${session.id.slice(-8)}`
                      : "Ready to chat"}
                  </span>
                  {isReactMode && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                      ReAct
                    </span>
                  )}
                  {plannerEnabled && (
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                      Planner
                    </span>
                  )}
                  <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                    {activeTools.length} tools
                  </span>
                  {facebookConnected && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs flex items-center gap-1">
                      <FaFacebook className="h-3 w-3" />
                      Meta
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <FaCog />
              </button>
            </div>
          </div>
        </header>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-6 mt-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-red-600 hover:text-red-800 underline text-sm"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden">
          <div
            ref={messagesContainerRef}
            className="h-full overflow-y-auto px-6 py-6"
          >
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.length === 0 && !session && (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                    <FaRobot className="text-white text-3xl" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-3">
                    Chat with {agent?.name}
                  </h2>
                  <p className="text-gray-600 mb-8 max-w-lg mx-auto text-lg">
                    {agent?.persona?.description ||
                      "I'm ready to help you with various tasks and answer your questions."}
                  </p>

                  {/* Agent Stats */}
                  <div className="flex justify-center space-x-6 mb-8">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {activeTools.length}
                      </div>
                      <div className="text-sm text-gray-500">Active Tools</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {isReactMode ? "ON" : "OFF"}
                      </div>
                      <div className="text-sm text-gray-500">ReAct Mode</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {plannerEnabled ? "ON" : "OFF"}
                      </div>
                      <div className="text-sm text-gray-500">Planner</div>
                    </div>
                  </div>

                  {/* Quick Start Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto mb-8">
                    <button
                      onClick={() =>
                        startConversation("Hello! What can you help me with?")
                      }
                      className="bg-blue-600 text-white px-6 py-4 rounded-xl hover:bg-blue-700 transition-all duration-200 hover:scale-105 shadow-md hover:shadow-lg"
                    >
                      <div className="flex items-center justify-center space-x-2">
                        <FaComment />
                        <span className="font-medium">Start Conversation</span>
                      </div>
                    </button>

                    <button
                      onClick={() =>
                        startConversation(
                          "What are your capabilities and available tools?"
                        )
                      }
                      className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-4 rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-200 hover:scale-105 shadow-md hover:shadow-lg"
                    >
                      <div className="flex items-center justify-center space-x-2">
                        <FaTools />
                        <span className="font-medium">Show Capabilities</span>
                      </div>
                    </button>
                  </div>

                  {/* Example Prompts */}
                  <div className="max-w-3xl mx-auto">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      Try these examples:
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {[
                        "Help me analyze this data",
                        "Search for recent news",
                        "Explain a complex topic",
                        "Generate creative content",
                        "Solve a problem step by step",
                        "Research and summarize",
                      ].map((prompt, index) => (
                        <button
                          key={index}
                          onClick={() => startConversation(prompt)}
                          className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors text-sm text-gray-700 hover:text-blue-700"
                        >
                          "{prompt}"
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div key={message.id} className="flex space-x-4">
                  {/* Avatar */}
                  <div className="flex-shrink-0">
                    {message.type === "user" ? (
                      <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                        <FaUser className="text-white text-sm" />
                      </div>
                    ) : message.type === "system" ? (
                      <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                        {getEventIcon(message.eventType)}
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <FaRobot className="text-white text-sm" />
                      </div>
                    )}
                  </div>

                  {/* Message Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900">
                        {message.type === "user"
                          ? "You"
                          : message.type === "system"
                          ? "System"
                          : agent?.name}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatTime(message.timestamp)}
                      </span>
                      {message.eventType && (
                        <span
                          className={`px-2 py-1 rounded-full text-xs ${getEventBadgeColor(
                            message.eventType
                          )}`}
                        >
                          {message.eventType.replace("_", " ")}
                        </span>
                      )}
                    </div>

                    {/* Enhanced Tool Call Rendering */}
                    {message.type === "system" &&
                    renderToolCallMessage(message) ? (
                      renderToolCallMessage(message)
                    ) : (
                      <div
                        className={`prose prose-sm max-w-none ${
                          message.type === "user"
                            ? "bg-blue-50 border border-blue-200 rounded-lg p-3"
                            : "bg-gray-50 border border-gray-200 rounded-lg p-3"
                        }`}
                      >
                        {/* Accordion for long user messages */}
                        {message.type === "user" &&
                        message.content.split("\n").length > 3 ? (
                          <div>
                            <div className="whitespace-pre-wrap text-gray-800 m-0">
                              {expandedMessages.has(message.id)
                                ? message.content
                                : message.content
                                    .split("\n")
                                    .slice(0, 3)
                                    .join("\n")}
                              {!expandedMessages.has(message.id) &&
                                message.content.split("\n").length > 3 && (
                                  <span className="text-gray-500">...</span>
                                )}
                            </div>
                            {message.content.split("\n").length > 3 && (
                              <button
                                onClick={() =>
                                  toggleMessageExpansion(message.id)
                                }
                                className="mt-2 text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
                              >
                                <span>
                                  {expandedMessages.has(message.id)
                                    ? "Show less"
                                    : "Show more"}
                                </span>
                                {expandedMessages.has(message.id) ? (
                                  <FaChevronUp />
                                ) : (
                                  <FaChevronDown />
                                )}
                              </button>
                            )}
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap text-gray-800 m-0">
                            {message.content}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Message Actions */}
                    {(message.type === "assistant" ||
                      message.type === "user") &&
                      message.content && (
                        <div className="flex items-center space-x-2 mt-2">
                          <button
                            onClick={() =>
                              copyToClipboard(message.content, message.id)
                            }
                            className={`p-1 transition-colors ${
                              copiedMessageId === message.id
                                ? "text-green-600"
                                : "text-gray-400 hover:text-gray-600"
                            }`}
                            title="Copy message"
                          >
                            {copiedMessageId === message.id ? (
                              <FaCheck className="text-xs" />
                            ) : (
                              <FaCopy className="text-xs" />
                            )}
                          </button>

                          {message.type === "assistant" && (
                            <>
                              <button
                                className="text-gray-400 hover:text-green-600 p-1"
                                title="Good response"
                              >
                                <FaThumbsUp className="text-xs" />
                              </button>
                              <button
                                className="text-gray-400 hover:text-red-600 p-1"
                                title="Poor response"
                              >
                                <FaThumbsDown className="text-xs" />
                              </button>
                            </>
                          )}
                        </div>
                      )}
                  </div>
                </div>
              ))}

              {/* Streaming Indicator */}
              {isStreaming && (
                <div className="flex space-x-4">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <FaRobot className="text-white text-sm" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">
                          {agent?.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          thinking...
                        </span>
                      </div>
                      <button
                        onClick={stopStreaming}
                        className="text-red-500 hover:text-red-700 text-xs bg-red-50 hover:bg-red-100 px-2 py-1 rounded transition-colors"
                        title="Stop generation"
                      >
                        <FaPause className="mr-1" />
                        Stop
                      </button>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white px-6 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        if (session) {
                          sendMessage();
                        } else {
                          startConversation(newMessage);
                        }
                      }
                    }}
                    placeholder="Type your message..."
                    className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
                    rows={1}
                    disabled={isStreaming}
                  />
                </div>
              </div>
              <button
                onClick={() => {
                  if (session) {
                    sendMessage();
                  } else {
                    startConversation(newMessage);
                  }
                }}
                disabled={!newMessage.trim() || isStreaming}
                className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isStreaming ? (
                  <FaSpinner className="animate-spin" />
                ) : (
                  <FaPaperPlane />
                )}
              </button>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Press Enter to send, Shift+Enter for new line</span>
              </div>
              <div className="flex items-center space-x-2">
                {activeTools.length > 0 && (
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full">
                    {activeTools.length} tools active
                  </span>
                )}
                {isReactMode && (
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    ReAct mode
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
