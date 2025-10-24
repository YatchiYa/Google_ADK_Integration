"use client";

import { ChatMessage as ChatMessageType } from "@/types/chat.types";
import { StreamingEventType } from "@/types/chat.types";
import { FaUser, FaRobot, FaCopy, FaCheck, FaChevronDown, FaChevronUp, FaThumbsUp, FaThumbsDown } from "react-icons/fa";
import { useState } from "react";
import ToolCallMessage from "./ToolCallMessage";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const isUser = message.type === "user";
  const isSystem = message.type === "system";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Handle system messages (tool calls, tool responses, thinking, etc.)
  if (isSystem && message.eventType) {
    return <ToolCallMessage message={message} />;
  }

  // Check if message is long and needs expansion - ONLY FOR USER MESSAGES
  const isLongMessage = isUser && message.content.split("\n").length > 3;
  const displayContent = expanded || !isLongMessage
    ? message.content
    : message.content.split("\n").slice(0, 3).join("\n") + "...";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`flex items-start space-x-3 max-w-3xl w-full ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? "bg-gradient-to-br from-gray-600 to-gray-800" 
            : "bg-gradient-to-br from-blue-500 to-cyan-500"
        }`}>
          {isUser ? (
            <FaUser className="text-white text-sm" />
          ) : (
            <FaRobot className="text-white text-sm" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? "items-end" : "items-start"} flex flex-col min-w-0`}>
          <div className={`px-4 py-3 rounded-2xl ${
            isUser
              ? "bg-gradient-to-r from-blue-500 to-cyan-500 text-white"
              : "bg-white border border-gray-200 text-gray-900"
          } shadow-sm max-w-full`}>
            <p className="text-sm whitespace-pre-wrap break-words">
              {displayContent}
            </p>
            
            {/* Expand/Collapse button ONLY for long USER messages */}
            {isLongMessage && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="mt-2 text-xs flex items-center space-x-1 text-white/80 hover:text-white"
              >
                <span>{expanded ? "Show less" : "Show more"}</span>
                {expanded ? <FaChevronUp /> : <FaChevronDown />}
              </button>
            )}
          </div>

          {/* Message Actions */}
          <div className="flex items-center space-x-2 mt-2 ml-2">
            <button
              onClick={handleCopy}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
              title="Copy message"
            >
              {copied ? <FaCheck className="text-green-500" /> : <FaCopy />}
            </button>
            
            {/* Thumbs up/down for assistant messages */}
            {!isUser && (
              <>
                <button
                  className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-gray-100 rounded transition-colors"
                  title="Good response"
                >
                  <FaThumbsUp className="text-xs" />
                </button>
                <button
                  className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-gray-100 rounded transition-colors"
                  title="Poor response"
                >
                  <FaThumbsDown className="text-xs" />
                </button>
              </>
            )}
            
            <span className="text-xs text-gray-400">
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
