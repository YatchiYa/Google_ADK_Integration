"use client";

import { Agent } from "@/types/agent.types";
import { ChatSession } from "@/types/chat.types";
import { FaPlus, FaComment, FaRobot, FaTimes, FaTrash } from "react-icons/fa";
import { useState } from "react";

interface ChatSidebarProps {
  agents: Agent[];
  conversations: ChatSession[];
  currentAgentId: string;
  onAgentSelect: (agentId: string) => void;
  onNewChat: () => void;
  onConversationSelect: (conversationId: string) => void;
  onDeleteConversation?: (conversationId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatSidebar({
  agents,
  conversations,
  currentAgentId,
  onAgentSelect,
  onNewChat,
  onConversationSelect,
  onDeleteConversation,
  isOpen,
  onClose
}: ChatSidebarProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    if (!onDeleteConversation) return;
    
    if (confirm("Are you sure you want to delete this conversation?")) {
      setDeletingId(conversationId);
      try {
        await onDeleteConversation(conversationId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 w-80 bg-white border-r border-gray-200 z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FaTimes className="text-gray-600" />
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-4">
            <button
              onClick={onNewChat}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all shadow-sm hover:shadow-md"
            >
              <FaPlus />
              <span className="font-medium">New Chat</span>
            </button>
          </div>

          {/* Agents List */}
          <div className="px-4 mb-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Agents
            </h3>
            <div className="space-y-1">
              {agents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => onAgentSelect(agent.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    agent.id === currentAgentId
                      ? "bg-blue-50 text-blue-600"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  <FaRobot className="text-sm" />
                  <span className="text-sm font-medium truncate">{agent.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto px-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Recent Chats
            </h3>
            <div className="space-y-1">
              {conversations.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">
                  No conversations yet
                </p>
              ) : (
                conversations.map((conv) => {
                  // Get first user message as title
                  const firstMessage = conv.messages?.find((m: any) => m.role === "user");
                  const title = firstMessage?.content?.substring(0, 40) || conv.id.slice(-8);
                  const isDeleting = deletingId === conv.id;

                  return (
                    <div
                      key={conv.id}
                      className="group relative w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <button
                        onClick={() => onConversationSelect(conv.id)}
                        disabled={isDeleting}
                        className="flex-1 flex items-center space-x-3 text-left min-w-0"
                      >
                        <FaComment className="text-sm flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {title}{title.length >= 40 ? "..." : ""}
                          </p>
                          <p className="text-xs text-gray-500 truncate">
                            {new Date(conv.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </button>
                      
                      {/* Delete Button */}
                      {onDeleteConversation && (
                        <button
                          onClick={(e) => handleDelete(e, conv.id)}
                          disabled={isDeleting}
                          className="opacity-0 group-hover:opacity-100 p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-all flex-shrink-0"
                          title="Delete conversation"
                        >
                          {isDeleting ? (
                            <div className="w-3 h-3 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <FaTrash className="text-xs" />
                          )}
                        </button>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
