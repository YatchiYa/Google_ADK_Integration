"use client";

import { Agent } from "@/types/agent.types";
import { FaRobot, FaChevronDown, FaChevronUp } from "react-icons/fa";
import { useState } from "react";

interface AgentSwitcherProps {
  currentAgent: Agent | null;
  availableAgents: Agent[];
  onAgentSelect: (agentId: string) => void;
}

export default function AgentSwitcher({
  currentAgent,
  availableAgents,
  onAgentSelect,
}: AgentSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <FaRobot className="text-blue-500" />
        <span className="text-sm font-medium text-gray-700 truncate max-w-32">
          {currentAgent?.name || "Select Agent"}
        </span>
        {isOpen ? <FaChevronUp className="text-gray-400" /> : <FaChevronDown className="text-gray-400" />}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-80 overflow-y-auto">
            {availableAgents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => {
                  onAgentSelect(agent.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center space-x-3 p-3 hover:bg-gray-50 transition-colors text-left ${
                  agent.id === currentAgent?.id
                    ? "bg-blue-50 border-l-4 border-blue-500"
                    : ""
                }`}
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <FaRobot className="text-white text-sm" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 text-sm truncate">
                    {agent.name}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {agent.description || agent.persona?.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
