"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthService } from "@/services/auth.service";
import { AgentService } from "@/services/agent.service";
import type { Agent } from "@/types/agent.types";
import AgentCard from "@/components/agents/AgentCard";
import CreateAgentModal from "@/components/agents/CreateAgentModal";
import {
  FaRobot,
  FaPlus,
  FaComments,
  FaTools,
  FaStore,
  FaLightbulb,
  FaRocket,
} from "react-icons/fa";

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthAndLoadData();
  }, []);

  const checkAuthAndLoadData = async () => {
    try {
      const authStatus = await AuthService.checkAuth();
      setIsAuthenticated(authStatus);

      if (authStatus) {
        await loadAgents();
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const loadAgents = async (isRefresh = false) => {
    try {
      setError(null);
      if (isRefresh) {
        setRefreshing(true);
      }
      const agentsData = await AgentService.getAgents();
      console.log("Loaded agents:", agentsData);
      setAgents(Array.isArray(agentsData) ? agentsData : []);
    } catch (error) {
      console.error("Failed to load agents:", error);
      setError(
        error instanceof Error ? error.message : "Failed to load agents"
      );
      setAgents([]);
    } finally {
      if (isRefresh) {
        setRefreshing(false);
      }
    }
  };

  const handleLogin = async () => {
    try {
      await AuthService.login("admin", "admin123");
      setIsAuthenticated(true);
      await loadAgents();
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleAgentCreated = (newAgent: Agent) => {
    console.log("Agent created:", newAgent);
    setAgents((prev) => {
      const currentAgents = Array.isArray(prev) ? prev : [];
      return [...currentAgents, newAgent];
    });
    setShowCreateModal(false);
    loadAgents();
  };

  const handleStartChat = (agentId: string) => {
    router.push(`/chat/${agentId}`);
  };

  useEffect(() => {
    handleLogin();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full border-4 border-blue-200"></div>
            <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
          </div>
          <p className="text-blue-600 font-semibold">
            Loading your AI marketplace...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-3xl shadow-2xl p-10 border border-blue-100">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
                <FaStore className="text-white text-3xl" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-3">
                AI Agent Marketplace
              </h1>
              <p className="text-gray-600 mb-8 leading-relaxed">
                Discover, create, and deploy intelligent AI agents with powerful
                tools and seamless conversations
              </p>
              <button
                onClick={handleLogin}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-4 px-6 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
              >
                Login to Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
      {/* Modern Header */}
      <header className="bg-white/80 backdrop-blur-xl shadow-lg border-b border-blue-100/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                <FaStore className="text-white text-xl" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  AI Agent Marketplace
                </h1>
                <p className="text-gray-600 text-sm font-medium">
                  Discover & Deploy Intelligent Agents
                </p>
              </div>
            </div>

            <nav className="flex items-center gap-2">
              <button
                onClick={() => router.push("/agents")}
                className="flex items-center gap-2 px-5 py-2.5 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200 font-medium"
              >
                <FaRobot />
                <span>Agents</span>
              </button>
              <button
                onClick={() => router.push("/tools")}
                className="flex items-center gap-2 px-5 py-2.5 text-gray-700 hover:text-cyan-600 hover:bg-cyan-50 rounded-xl transition-all duration-200 font-medium"
              >
                <FaTools />
                <span>Tools</span>
              </button>
              <button
                onClick={() => router.push("/chat")}
                className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 font-semibold hover:scale-105"
              >
                <FaComments />
                <span>Start Chat</span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-6">
            <FaRocket className="text-blue-600" />
            Welcome to Your AI Hub
          </div>
          <h2 className="text-5xl font-bold text-gray-900 mb-4 text-balance">
            Build the Future with{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              AI Agents
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto text-pretty leading-relaxed">
            Create, manage, and deploy intelligent AI agents with powerful tools
            and seamless conversations. Your marketplace for AI innovation.
          </p>
        </div>

        {/* Enhanced Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="group bg-white rounded-2xl shadow-lg p-8 border border-blue-100 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-blue-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-700 group-hover:text-blue-600 transition-colors mb-2">
                  AI Agents
                </h3>
                <p className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  {agents?.length || 0}
                </p>
                <p className="text-sm text-gray-500 mt-2 font-medium">
                  Active & ready to assist
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:shadow-xl group-hover:shadow-blue-500/40 transition-all duration-300 group-hover:scale-110">
                <FaRobot className="text-white text-2xl" />
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3.5 px-6 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 flex items-center justify-center font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
            >
              <FaPlus className="mr-2" />
              Create New Agent
            </button>
          </div>

          <div className="group bg-white rounded-2xl shadow-lg p-8 border border-cyan-100 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-cyan-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-700 group-hover:text-cyan-600 transition-colors mb-2">
                  Smart Tools
                </h3>
                <p className="text-5xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                  24
                </p>
                <p className="text-sm text-gray-500 mt-2 font-medium">
                  Powerful capabilities
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:shadow-xl group-hover:shadow-cyan-500/40 transition-all duration-300 group-hover:scale-110">
                <FaTools className="text-white text-2xl" />
              </div>
            </div>
            <button
              onClick={() => router.push("/tools")}
              className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3.5 px-6 rounded-xl hover:from-cyan-700 hover:to-blue-700 transition-all duration-200 font-semibold shadow-lg shadow-cyan-500/30 hover:shadow-xl hover:shadow-cyan-500/40 hover:scale-105"
            >
              Explore Tools
            </button>
          </div>

          <div className="group bg-white rounded-2xl shadow-lg p-8 border border-sky-100 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 hover:border-sky-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-700 group-hover:text-sky-600 transition-colors mb-2">
                  Conversations
                </h3>
                <p className="text-5xl font-bold bg-gradient-to-r from-sky-600 to-blue-600 bg-clip-text text-transparent">
                  {agents?.reduce(
                    (sum, agent) => sum + (agent.usage_count || 0),
                    0
                  ) || 0}
                </p>
                <p className="text-sm text-gray-500 mt-2 font-medium">
                  Total interactions
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-sky-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-sky-500/30 group-hover:shadow-xl group-hover:shadow-sky-500/40 transition-all duration-300 group-hover:scale-110">
                <FaComments className="text-white text-2xl" />
              </div>
            </div>
            <button
              onClick={() => router.push("/chat")}
              className="w-full bg-gradient-to-r from-sky-600 to-blue-600 text-white py-3.5 px-6 rounded-xl hover:from-sky-700 hover:to-blue-700 transition-all duration-200 font-semibold shadow-lg shadow-sky-500/30 hover:shadow-xl hover:shadow-sky-500/40 hover:scale-105"
            >
              Start Chatting
            </button>
          </div>
        </div>

        {/* Featured Agents Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-blue-100">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Your AI Agents
              </h2>
              <p className="text-gray-600">
                Manage and interact with your intelligent assistants
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => loadAgents(true)}
                className="bg-blue-50 text-blue-600 px-5 py-2.5 rounded-xl hover:bg-blue-100 transition-all duration-200 font-medium border border-blue-200"
                disabled={refreshing}
              >
                {refreshing ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
                ) : (
                  "Refresh"
                )}
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-2.5 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 flex items-center gap-2 font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
              >
                <FaPlus />
                Create Agent
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-5 bg-red-50 border-2 border-red-200 rounded-xl">
              <p className="text-red-700 font-medium">{error}</p>
              <button
                onClick={loadAgents}
                className="mt-3 text-red-600 hover:text-red-800 underline font-semibold"
              >
                Try again
              </button>
            </div>
          )}

          {agents?.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
                <FaLightbulb className="text-blue-600 text-4xl" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                No agents yet
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Create your first AI agent to unlock the power of intelligent
                automation
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105"
              >
                Create Your First Agent
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents?.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onStartChat={handleStartChat}
                  onEdit={() => router.push(`/agents/${agent.id}/edit`)}
                  onDelete={() => {
                    /* Handle delete */
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Agent Modal */}
      {showCreateModal && (
        <CreateAgentModal
          onClose={() => setShowCreateModal(false)}
          onAgentCreated={handleAgentCreated}
        />
      )}
    </div>
  );
}
