"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Agent } from "@/types/agent.types";
import { AgentService } from "@/services/agent.service";
import { FaRobot, FaComments, FaArrowRight } from "react-icons/fa";

export default function ChatPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setError(null);
      const agentsData = await AgentService.getAgents();
      console.log("Loaded agents in chat page:", agentsData); // Debug log
      setAgents(Array.isArray(agentsData) ? agentsData : []);
    } catch (error) {
      console.error("Failed to load agents:", error);
      setError(error instanceof Error ? error.message : "Failed to load agents");
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartChat = (agentId: string) => {
    router.push(`/chat/${agentId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <FaComments className="mr-3 text-green-600" />
                Start a Conversation
              </h1>
              <p className="text-gray-600 mt-1">
                Choose an agent to begin chatting
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
            <button
              onClick={loadAgents}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {agents?.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <FaRobot className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No agents available
            </h3>
            <p className="text-gray-600 mb-6">
              Create an agent first to start chatting
            </p>
            <button
              onClick={() => router.push("/agents")}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Agent Management
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents?.map((agent) => (
              <div
                key={agent.id}
                className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-1 cursor-pointer"
                onClick={() => handleStartChat(agent.id)}
              >
                {/* Agent Header */}
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                    <FaRobot className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg">
                      {agent.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {agent.persona?.name || "AI Assistant"}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {agent.persona?.description ||
                    "Ready to help with various tasks"}
                </p>

                {/* Tools */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {agent.tools && agent.tools.length > 0 ? (
                      agent.tools.slice(0, 3).map((tool) => (
                        <span
                          key={tool}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {tool.startsWith("agent:") ? tool.substring(6) : tool}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-gray-400 italic">
                        No tools
                      </span>
                    )}
                    {agent.tools && agent.tools.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        +{agent.tools.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Chat Button */}
                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    {agent.usage_count || 0} conversations
                  </div>
                  <div className="flex items-center text-green-600 font-medium">
                    <span className="mr-2">Start Chat</span>
                    <FaArrowRight />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
