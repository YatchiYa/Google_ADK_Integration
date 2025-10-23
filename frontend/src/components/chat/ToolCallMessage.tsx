"use client";

import { ChatMessage } from "@/types/chat.types";
import { StreamingEventType } from "@/types/chat.types";
import { FaWrench, FaCheck, FaBrain, FaChevronDown, FaChevronUp } from "react-icons/fa";
import { useState } from "react";
import AuthenticatedImage from "@/components/AuthenticatedImage";

interface ToolCallMessageProps {
  message: ChatMessage;
}

export default function ToolCallMessage({ message }: ToolCallMessageProps) {
  const [showDetails, setShowDetails] = useState(false);

  // Tool Call Message
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

    return (
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg my-2">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <FaWrench className="text-blue-500 animate-spin" />
            <span className="font-medium text-blue-800">Tool Call</span>
            <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full">
              {toolName}
            </span>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
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
                <div className="text-xs bg-blue-200 p-2 rounded font-mono overflow-auto max-h-40">
                  {JSON.stringify(toolArgs, null, 2)}
                </div>
              </div>
            )}
            {callId && (
              <div>
                <div className="text-xs font-medium text-blue-800 mb-1">
                  Call ID:
                </div>
                <div className="text-xs text-blue-600 font-mono">{callId}</div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Tool Response Message
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

    const hasImageResult =
      toolResult && (toolResult.main_image_path || toolResult.main_image_url);

    return (
      <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg my-2">
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
            onClick={() => setShowDetails(!showDetails)}
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

        {/* Tool Summary */}
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
              {toolResult.total_images && (
                <div>
                  <strong>Images Generated:</strong> {toolResult.total_images}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Generated Images */}
        {hasImageResult && (
          <div className="mt-3 mb-3">
            <div className="bg-white p-3 rounded-lg border">
              <div className="text-xs font-medium text-green-800 mb-2">
                Generated Image:
              </div>
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
                className="max-w-full h-auto rounded-lg shadow-sm border"
                style={{ maxHeight: "400px" }}
              />
            </div>
          </div>
        )}

        {/* Expandable Details */}
        {showDetails && toolResult && (
          <div className="mt-3 space-y-3">
            <div className="bg-white p-3 rounded-lg border">
              <div className="text-xs font-medium text-green-800 mb-2">
                Tool Result:
              </div>
              <div className="text-xs bg-gray-100 p-2 rounded font-mono max-h-40 overflow-y-auto">
                {JSON.stringify(toolResult, null, 2)}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Thinking Message
  if (message.eventType === StreamingEventType.THINKING) {
    return (
      <div className="bg-purple-50 border-l-4 border-purple-400 p-4 rounded-r-lg my-2">
        <div className="flex items-center space-x-2 mb-2">
          <FaBrain className="text-purple-500 animate-pulse" />
          <span className="font-medium text-purple-800">Thinking</span>
        </div>
        <div className="text-sm text-purple-700 italic">{message.content}</div>
      </div>
    );
  }

  // Error Message
  if (message.eventType === StreamingEventType.ERROR) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg my-2">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-red-500 text-lg">⚠️</span>
          <span className="font-medium text-red-800">Error</span>
        </div>
        <div className="text-sm text-red-700">{message.content}</div>
      </div>
    );
  }

  return null;
}
