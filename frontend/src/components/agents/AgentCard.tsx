"use client";

import type { Agent } from "@/types/agent.types";
import {
  FaRobot,
  FaComments,
  FaEdit,
  FaTrash,
  FaCog,
  FaUser,
  FaBrain,
  FaCheckCircle,
  FaStar,
} from "react-icons/fa";

interface AgentCardProps {
  agent: Agent;
  onStartChat: (agentId: string) => void;
  onEdit: (agentId: string) => void;
  onDelete: (agentId: string) => void;
}

export default function AgentCard({
  agent,
  onStartChat,
  onEdit,
  onDelete,
}: AgentCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getAgentTypeColor = (type?: string) => {
    switch (type) {
      case "react":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "sequential":
        return "bg-cyan-50 text-cyan-700 border-cyan-200";
      case "parallel":
        return "bg-sky-50 text-sky-700 border-sky-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const getAgentTypeLabel = (type?: string) => {
    switch (type) {
      case "react":
        return "ReAct Planner";
      case "sequential":
        return "Sequential";
      case "parallel":
        return "Parallel";
      default:
        return "Standard";
    }
  };

  return (
    <div className="group bg-white rounded-2xl shadow-sm hover:shadow-2xl transition-all duration-300 overflow-hidden border border-blue-100/50 hover:border-blue-300 hover:-translate-y-1">
      {/* Header with gradient background */}
      <div className="relative bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50 p-6 pb-20">
        {/* Agent Type Badge */}
        {agent.agent_type && (
          <div className="absolute top-4 right-4">
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${getAgentTypeColor(
                agent.agent_type
              )} backdrop-blur-sm`}
            >
              <FaCog className="text-xs" />
              {getAgentTypeLabel(agent.agent_type)}
            </span>
          </div>
        )}

        {/* Agent Avatar and Info */}
        <div className="flex items-start gap-4">
          <div className="relative">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:shadow-xl group-hover:shadow-blue-500/40 transition-all duration-300">
              <FaRobot className="text-white text-2xl" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
              <FaCheckCircle className="text-white text-xs" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-xl mb-1 truncate group-hover:text-blue-600 transition-colors">
              {agent.name}
            </h3>
            <p className="text-sm text-gray-600 flex items-center gap-1.5">
              <FaUser className="text-xs text-blue-500" />
              {agent.persona?.name || "AI Assistant"}
            </p>

            {/* Rating */}
            <div className="flex items-center gap-1 mt-2">
              <div className="flex items-center gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <FaStar key={i} className="text-yellow-400 text-xs" />
                ))}
              </div>
              <span className="text-xs text-gray-500 ml-1">5.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 -mt-14 relative">
        {/* Description Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-4">
          <p className="text-sm text-gray-700 line-clamp-3 leading-relaxed">
            {agent.persona?.description || "No description available"}
          </p>
        </div>

        {/* Personality & Communication Style */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {agent.persona?.personality && (
            <div className="bg-blue-50/50 rounded-lg p-3 border border-blue-100">
              <div className="flex items-center gap-2 text-xs text-blue-600 font-medium mb-1">
                <FaBrain className="text-sm" />
                <span>Personality</span>
              </div>
              <p className="text-xs text-gray-700 font-medium truncate">
                {agent.persona.personality}
              </p>
            </div>
          )}
          {agent.persona?.communication_style && (
            <div className="bg-cyan-50/50 rounded-lg p-3 border border-cyan-100">
              <div className="flex items-center gap-2 text-xs text-cyan-600 font-medium mb-1">
                <FaComments className="text-sm" />
                <span>Style</span>
              </div>
              <p className="text-xs text-gray-700 font-medium capitalize truncate">
                {agent.persona.communication_style}
              </p>
            </div>
          )}
        </div>

        {/* Tools */}
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Tools & Capabilities
          </p>
          <div className="flex flex-wrap gap-2">
            {agent.tools && agent.tools.length > 0 ? (
              agent.tools.slice(0, 4).map((tool) => (
                <span
                  key={tool}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 hover:scale-105 ${
                    tool.startsWith("agent:")
                      ? "bg-purple-50 text-purple-700 border border-purple-200"
                      : "bg-blue-50 text-blue-700 border border-blue-200"
                  }`}
                >
                  {tool.startsWith("agent:") ? (
                    <FaRobot className="text-xs" />
                  ) : (
                    <FaCog className="text-xs" />
                  )}
                  {tool.startsWith("agent:") ? tool.substring(6) : tool}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-400 italic">
                No tools attached
              </span>
            )}
            {agent.tools && agent.tools.length > 4 && (
              <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-50 text-gray-600 border border-gray-200">
                +{agent.tools.length - 4} more
              </span>
            )}
          </div>
        </div>

        {/* Expertise */}
        {agent.persona?.expertise && agent.persona.expertise.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Expertise
            </p>
            <div className="flex flex-wrap gap-2">
              {agent.persona.expertise.slice(0, 3).map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-50 to-cyan-50 text-blue-700 text-xs rounded-lg font-medium border border-blue-200"
                >
                  {skill}
                </span>
              ))}
              {agent.persona.expertise.length > 3 && (
                <span className="inline-flex items-center px-3 py-1.5 bg-gray-50 text-gray-600 text-xs rounded-lg font-medium border border-gray-200">
                  +{agent.persona.expertise.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4 pb-4 border-b border-gray-100">
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
            Created {formatDate(agent.created_at)}
          </span>
          <span className="font-semibold text-blue-600">
            {agent.usage_count || 0} chats
          </span>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onStartChat(agent.id)}
            className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 px-4 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 flex items-center justify-center text-sm font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
          >
            <FaComments className="mr-2" />
            Start Chat
          </button>
          <button
            onClick={() => onEdit(agent.id)}
            className="bg-white border-2 border-blue-200 text-blue-600 py-3 px-4 rounded-xl hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 hover:scale-105"
          >
            <FaEdit />
          </button>
          <button
            onClick={() => onDelete(agent.id)}
            className="bg-white border-2 border-red-200 text-red-600 py-3 px-4 rounded-xl hover:bg-red-50 hover:border-red-300 transition-all duration-200 hover:scale-105"
          >
            <FaTrash />
          </button>
        </div>
      </div>
    </div>
  );
}
