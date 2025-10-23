"use client";

import { Agent } from "@/types/agent.types";
import { FaTimes, FaCog, FaTools, FaToggleOn, FaToggleOff, FaFacebook } from "react-icons/fa";
import FacebookConnectionPanel from "@/components/FacebookConnectionPanel";

interface ChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  agent: Agent | null;
  availableTools: string[];
  activeTools: string[];
  onToggleTool: (toolName: string) => void;
  isReactMode: boolean;
  plannerEnabled: boolean;
  onToggleReactMode: () => void;
  onTogglePlanner: () => void;
  agentId: string;
  sessionId?: string;
  onFacebookConnectionChange: (connected: boolean) => void;
}

export default function ChatDrawer({
  isOpen,
  onClose,
  agent,
  availableTools,
  activeTools,
  onToggleTool,
  isReactMode,
  plannerEnabled,
  onToggleReactMode,
  onTogglePlanner,
  agentId,
  sessionId,
  onFacebookConnectionChange,
}: ChatDrawerProps) {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-500 to-cyan-500">
            <h2 className="text-lg font-semibold text-white">Settings & Tools</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors text-white"
            >
              <FaTimes />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            {/* Agent Configuration */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2 mb-4">
                <FaCog className="text-blue-500" />
                <h3 className="font-medium text-gray-800">Agent Configuration</h3>
              </div>

              <div className="space-y-3">
                {/* Reflexion Agent Toggle */}
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                  <div>
                    <div className="text-sm font-semibold text-gray-800">Activate Reflexion Agent</div>
                    <div className="text-xs text-gray-600">Advanced reasoning with planning & reflection</div>
                  </div>
                  <button
                    onClick={onToggleReactMode}
                    className={`relative inline-flex h-7 w-12 items-center rounded-full transition-all duration-300 shadow-md ${
                      isReactMode 
                        ? "bg-gradient-to-r from-purple-600 to-blue-600" 
                        : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-300 shadow-sm ${
                        isReactMode ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Tools Panel */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2 mb-4">
                <FaTools className="text-blue-500" />
                <h3 className="font-medium text-gray-800">Tools</h3>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  {activeTools.length} active
                </span>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {availableTools.map((tool) => {
                  const isActive = activeTools.includes(tool);
                  return (
                    <div
                      key={tool}
                      className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
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
                        onClick={() => onToggleTool(tool)}
                        className={`ml-2 text-xl transition-colors ${
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

            {/* Facebook Connection */}
            <div className="p-4">
              <div className="flex items-center space-x-2 mb-4">
                <FaFacebook className="text-blue-600" />
                <h3 className="font-medium text-gray-800">Facebook Integration</h3>
              </div>
              <FacebookConnectionPanel
                agentId={agentId}
                sessionId={sessionId}
                onConnectionChange={onFacebookConnectionChange}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
