"use client";

import { useState } from "react";
import { FaChevronDown, FaChevronUp, FaCheckCircle, FaSpinner, FaBrain } from "react-icons/fa";

interface StreamingEventProps {
  type: "tool_call" | "tool_response" | "thinking" | "typing";
  toolName?: string;
  content?: string;
  metadata?: any;
  isComplete?: boolean;
}

export default function StreamingEvent({
  type,
  toolName,
  content,
  metadata,
  isComplete = false,
}: StreamingEventProps) {
  const [showDetails, setShowDetails] = useState(false);

  // Get icon and color based on type
  const getEventStyle = () => {
    switch (type) {
      case "tool_call":
        return {
          icon: isComplete ? <FaCheckCircle className="text-green-500" /> : <FaSpinner className="text-yellow-500 animate-spin" />,
          bgColor: isComplete ? "bg-green-50" : "bg-yellow-50",
          borderColor: isComplete ? "border-green-200" : "border-yellow-200",
          textColor: isComplete ? "text-green-800" : "text-yellow-800",
          label: isComplete ? "Completed" : "Starting",
        };
      case "tool_response":
        return {
          icon: <FaCheckCircle className="text-green-500" />,
          bgColor: "bg-green-50",
          borderColor: "border-green-200",
          textColor: "text-green-800",
          label: "Completed",
        };
      case "thinking":
        return {
          icon: <FaBrain className="text-purple-500 animate-pulse" />,
          bgColor: "bg-purple-50",
          borderColor: "border-purple-200",
          textColor: "text-purple-800",
          label: "Thinking",
        };
      case "typing":
        return {
          icon: <FaSpinner className="text-blue-500 animate-spin" />,
          bgColor: "bg-blue-50",
          borderColor: "border-blue-200",
          textColor: "text-blue-800",
          label: "typing...",
        };
      default:
        return {
          icon: <FaSpinner className="text-gray-500 animate-spin" />,
          bgColor: "bg-gray-50",
          borderColor: "border-gray-200",
          textColor: "text-gray-800",
          label: "Processing",
        };
    }
  };

  const style = getEventStyle();

  // Format tool name for display
  const formatToolName = (name?: string) => {
    if (!name) return "";
    return name
      .replace(/_/g, " ")
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className={`my-2 rounded-lg border ${style.borderColor} ${style.bgColor} overflow-hidden transition-all duration-200`}>
      {/* Event Header - Always Visible */}
      <div className="flex items-center justify-between p-3">
        <div className="flex items-center space-x-3 flex-1">
          <div className="flex-shrink-0">
            {style.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className={`text-sm font-medium ${style.textColor}`}>
                {style.label}
              </span>
              {toolName && (
                <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full border border-gray-200">
                  {formatToolName(toolName)}
                </span>
              )}
            </div>
            {content && !showDetails && (
              <p className="text-xs text-gray-600 mt-1 truncate">
                {content.substring(0, 60)}...
              </p>
            )}
          </div>
        </div>

        {/* Toggle Details Button */}
        {(metadata || content) && (
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

      {/* Event Details - Collapsible */}
      {showDetails && (metadata || content) && (
        <div className="px-3 pb-3 border-t border-gray-200/50">
          {/* Content */}
          {content && (
            <div className="mt-2">
              <div className="text-xs font-medium text-gray-600 mb-1">Response:</div>
              <div className="text-sm text-gray-700 bg-white/60 rounded p-2 max-h-60 overflow-y-auto">
                {content}
              </div>
            </div>
          )}

          {/* Metadata */}
          {metadata && (
            <div className="mt-2">
              <div className="text-xs font-medium text-gray-600 mb-1">Details:</div>
              <div className="bg-white/60 rounded p-2 max-h-40 overflow-y-auto">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(metadata, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
