"use client";

import { Agent } from "@/types/agent.types";
import { FaRobot, FaBars, FaCog } from "react-icons/fa";
import AgentSwitcher from "./AgentSwitcher";

interface ChatHeaderProps {
  agent: Agent | null;
  availableAgents: Agent[];
  onMenuClick: () => void;
  onSettingsClick: () => void;
  onAgentSelect: (agentId: string) => void;
  isReactMode?: boolean;
  plannerEnabled?: boolean;
  activeToolsCount?: number;
  facebookConnected?: boolean;
}

export default function ChatHeader({
  agent,
  availableAgents,
  onMenuClick,
  onSettingsClick,
  onAgentSelect,
  isReactMode,
  plannerEnabled,
  activeToolsCount,
  facebookConnected,
}: ChatHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <FaBars className="text-gray-600" />
          </button>

          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
            <FaRobot className="text-white text-lg" />
          </div>

          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              {agent?.name || "Loading..."}
            </h1>
            <div className="flex items-center space-x-2 text-xs">
              {isReactMode && (
                <span className="bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 px-2 py-0.5 rounded-full font-medium">
                  🧠 Reflexion
                </span>
              )}
              {activeToolsCount !== undefined && activeToolsCount > 0 && (
                <span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full">
                  {activeToolsCount} tools
                </span>
              )}
              {facebookConnected && (
                <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                  Meta
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Agent Switcher */}
          <AgentSwitcher
            currentAgent={agent}
            availableAgents={availableAgents}
            onAgentSelect={onAgentSelect}
          />

          {/* Settings Button */}
          <button
            onClick={onSettingsClick}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings & Tools"
          >
            <FaCog />
          </button>
        </div>
      </div>
    </header>
  );
}
