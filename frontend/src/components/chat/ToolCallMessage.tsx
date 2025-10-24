"use client";

import { ChatMessage } from "@/types/chat.types";
import { StreamingEventType } from "@/types/chat.types";
import { FaCheckCircle, FaSpinner, FaBrain, FaChevronDown, FaChevronUp } from "react-icons/fa";
import { useState } from "react";
import AuthenticatedImage from "@/components/AuthenticatedImage";

interface ToolCallMessageProps {
  message: ChatMessage;
}

export default function ToolCallMessage({ message }: ToolCallMessageProps) {
  const [showDetails, setShowDetails] = useState(false);

  // Tool Call Message - Professional streaming style
  if (message.eventType === StreamingEventType.TOOL_CALL) {
    let toolName = "Unknown Tool";
    let toolArgs = {};
    let callId = "";

    try {
      if (message.metadata) {
        toolName = message.metadata.tool_name || toolName;
        toolArgs = message.metadata.tool_args || {};
        callId = message.metadata.call_id || "";
      } else {
        const match = message.content.match(/Calling tool: (\w+)/);
        if (match) toolName = match[1];
      }
    } catch (error) {
      console.error("Error parsing tool call metadata:", error);
    }

    // Format tool name
    const formatToolName = (name: string) => {
      return name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
    };

    return (
      <div className="my-2 rounded-lg border border-yellow-200 bg-yellow-50 overflow-hidden transition-all duration-200">
        {/* Header - Always Visible */}
        <div className="flex items-center justify-between p-3">
          <div className="flex items-center space-x-3 flex-1">
            <FaSpinner className="text-yellow-500 animate-spin flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-yellow-800">Starting</span>
                <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full border border-yellow-200">
                  {formatToolName(toolName)}
                </span>
              </div>
            </div>
          </div>
          {(Object.keys(toolArgs).length > 0 || callId) && (
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="ml-2 p-1.5 hover:bg-white/60 rounded transition-colors flex-shrink-0"
            >
              {showDetails ? (
                <FaChevronUp className="text-gray-500 text-xs" />
              ) : (
                <FaChevronDown className="text-gray-500 text-xs" />
              )}
            </button>
          )}
        </div>

        {/* Details - Collapsible */}
        {showDetails && (Object.keys(toolArgs).length > 0 || callId) && (
          <div className="px-3 pb-3 border-t border-yellow-200/50">
            {Object.keys(toolArgs).length > 0 && (
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-600 mb-1">Arguments:</div>
                <div className="bg-white/60 rounded p-2 max-h-40 overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(toolArgs, null, 2)}
                  </pre>
                </div>
              </div>
            )}
            {callId && (
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-600 mb-1">Call ID:</div>
                <div className="text-xs text-gray-600 font-mono bg-white/60 rounded p-2">{callId}</div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Tool Response Message - Professional streaming style
  if (message.eventType === StreamingEventType.TOOL_RESPONSE) {
    let toolName = "Unknown Tool";
    let toolResult = null;
    let rawResponse = null;
    let actualResult = null;

    try {
      if (message.metadata) {
        toolName = message.metadata.tool_name || toolName;
        toolResult = message.metadata.tool_result;
        rawResponse = message.metadata.raw_response;
        
        // Extract actual result - check rawResponse.result if toolResult is empty
        if (rawResponse && rawResponse.result) {
          actualResult = rawResponse.result;
        } else if (toolResult && Object.keys(toolResult).length > 0) {
          actualResult = toolResult;
        }
      }
    } catch (error) {
      console.error("Error parsing tool response metadata:", error);
    }

    const hasImageResult =
      toolResult && (toolResult.main_image_path || toolResult.main_image_url);

    // Format tool name
    const formatToolName = (name: string) => {
      return name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
    };

    return (
      <div className="my-2 rounded-lg border border-green-200 bg-green-50 overflow-hidden transition-all duration-200">
        {/* Header - Always Visible */}
        <div className="flex items-center justify-between p-3">
          <div className="flex items-center space-x-3 flex-1">
            <FaCheckCircle className="text-green-500 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 flex-wrap">
                <span className="text-sm font-medium text-green-800">Completed</span>
                <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full border border-green-200">
                  {formatToolName(toolName)}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="ml-2 p-1.5 hover:bg-white/60 rounded transition-colors flex-shrink-0"
          >
            {showDetails ? (
              <FaChevronUp className="text-gray-500 text-xs" />
            ) : (
              <FaChevronDown className="text-gray-500 text-xs" />
            )}
          </button>
        </div>

        {/* Generated Images - Always show if available */}
        {hasImageResult && (
          <div className="px-3 pb-3">
            <div className="bg-white/60 rounded-lg p-2">
              <AuthenticatedImage
                src={
                  toolResult.main_image_url?.startsWith("http")
                    ? toolResult.main_image_url
                    : `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${
                        toolResult.main_image_url ||
                        `/api/v1/images/serve/${
                          toolResult.main_image_filename ||
                          toolResult.main_image_path?.split("/").pop()
                        }`
                      }`
                }
                alt={toolResult.prompt || "Generated image"}
                className="max-w-full h-auto rounded-lg shadow-sm"
                style={{ maxHeight: "400px" }}
              />
            </div>
          </div>
        )}

        {/* Collapsible Details */}
        {showDetails && (
          <div className="px-3 pb-3 border-t border-green-200/50">
            {/* Tool Summary */}
            {toolResult && (
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-600 mb-1">Tool Summary:</div>
                <div className="bg-white/60 rounded p-2">
                  <div className="text-xs text-gray-700 space-y-1">
                    {toolResult.success !== undefined && (
                      <div>
                        <strong>Status:</strong> {toolResult.success ? "✅ Success" : "❌ Failed"}
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
                    {toolResult.total_images && (
                      <div>
                        <strong>Images Generated:</strong> {toolResult.total_images}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Tool Result - Show actual result from rawResponse.result or toolResult */}
            {actualResult && (
              <div className="mt-2">
                <div className="text-xs font-medium text-green-800 mb-1">📄 Tool Summary:</div>
                <div className="bg-white/80 rounded p-3 border border-green-200">
                  <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                    {typeof actualResult === 'string' ? actualResult : JSON.stringify(actualResult, null, 2)}
                  </div>
                </div>
              </div>
            )}

            {/* Full Response (if different from actual result) */}
            {message.content && message.content !== actualResult && (
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-600 mb-1">Response:</div>
                <div className="bg-white/60 rounded p-2 max-h-60 overflow-y-auto">
                  <div className="text-xs text-gray-700 whitespace-pre-wrap">
                    {message.content}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Thinking Message - Professional streaming style
  if (message.eventType === StreamingEventType.THINKING) {
    return (
      <div className="my-2 rounded-lg border border-purple-200 bg-purple-50 overflow-hidden transition-all duration-200">
        <div className="flex items-center space-x-3 p-3">
          <FaBrain className="text-purple-500 animate-pulse flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <span className="text-sm font-medium text-purple-800">Thinking...</span>
          </div>
        </div>
      </div>
    );
  }

  // Error Message
  if (message.eventType === StreamingEventType.ERROR) {
    return (
      <div className="my-2 rounded-lg border border-red-200 bg-red-50 overflow-hidden transition-all duration-200">
        <div className="flex items-center space-x-3 p-3">
          <span className="text-red-500 text-lg flex-shrink-0">⚠️</span>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-red-800 mb-1">Error</div>
            <div className="text-xs text-red-700">{message.content}</div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
