"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { Agent } from "@/types/agent.types";
import { AgentService } from "@/services/agent.service";
import CreateAgentModal from "@/components/agents/CreateAgentModal";
import {
  FaRobot,
  FaPlus,
  FaSearch,
  FaFilter,
  FaSync,
  FaStar,
  FaClock,
  FaUsers,
  FaTimes,
  FaEdit,
  FaComments,
  FaGoogle,
  FaDatabase,
  FaCode,
  FaCalculator,
  FaFileAlt,
  FaImage,
  FaMusic,
  FaVideo,
  FaGlobe,
  FaShoppingCart,
  FaEnvelope,
  FaCalendar,
  FaMapMarkerAlt,
  FaNewspaper,
  FaBookOpen,
  FaLanguage,
  FaChartBar,
  FaPalette,
  FaGamepad,
  FaTools,
  FaWeebly,
} from "react-icons/fa";

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"name" | "created_at" | "usage_count">(
    "name"
  );
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showAgentModal, setShowAgentModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Tool icon mapping
  const getToolIcon = (toolName: string) => {
    const toolLower = toolName.toLowerCase();
    if (toolLower.includes("google") || toolLower.includes("search"))
      return FaGoogle;
    if (toolLower.includes("database") || toolLower.includes("sql"))
      return FaDatabase;
    if (toolLower.includes("code") || toolLower.includes("programming"))
      return FaCode;
    if (toolLower.includes("calculator") || toolLower.includes("math"))
      return FaCalculator;
    if (toolLower.includes("file") || toolLower.includes("document"))
      return FaFileAlt;
    if (toolLower.includes("image") || toolLower.includes("photo"))
      return FaImage;
    if (toolLower.includes("music") || toolLower.includes("audio"))
      return FaMusic;
    if (toolLower.includes("video")) return FaVideo;
    if (toolLower.includes("web") || toolLower.includes("url")) return FaGlobe;
    if (toolLower.includes("shop") || toolLower.includes("product"))
      return FaShoppingCart;
    if (toolLower.includes("email") || toolLower.includes("mail"))
      return FaEnvelope;
    if (toolLower.includes("calendar") || toolLower.includes("schedule"))
      return FaCalendar;
    if (toolLower.includes("map") || toolLower.includes("location"))
      return FaMapMarkerAlt;
    if (toolLower.includes("weather")) return FaWeebly;
    if (toolLower.includes("news")) return FaNewspaper;
    if (toolLower.includes("book") || toolLower.includes("read"))
      return FaBookOpen;
    if (toolLower.includes("language") || toolLower.includes("translate"))
      return FaLanguage;
    if (toolLower.includes("chart") || toolLower.includes("analytics"))
      return FaChartBar;
    if (toolLower.includes("design") || toolLower.includes("creative"))
      return FaPalette;
    if (toolLower.includes("game")) return FaGamepad;
    return FaRobot; // Default icon
  };

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    filterAndSortAgents();
  }, [agents, searchTerm, filterType, sortBy]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const agentsData = await AgentService.getAgents();
      console.log("Loaded agents in agents page:", agentsData); // Debug log
      setAgents(Array.isArray(agentsData) ? agentsData : []);
    } catch (error) {
      console.error("Failed to load agents:", error);
      setError(
        error instanceof Error ? error.message : "Failed to load agents"
      );
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortAgents = () => {
    if (!Array.isArray(agents)) {
      setFilteredAgents([]);
      return;
    }
    let filtered = [...agents];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (agent) =>
          agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          agent.persona?.description
            ?.toLowerCase()
            .includes(searchTerm.toLowerCase()) ||
          agent.persona?.expertise?.some((skill) =>
            skill.toLowerCase().includes(searchTerm.toLowerCase())
          )
      );
    }

    // Apply type filter
    if (filterType !== "all") {
      filtered = filtered.filter((agent) => {
        if (filterType === "standard") return !agent.agent_type;
        return agent.agent_type === filterType;
      });
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "created_at":
          return (
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
        case "usage_count":
          return (b.usage_count || 0) - (a.usage_count || 0);
        case "name":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    setFilteredAgents(filtered);
  };

  const handleAgentCreated = (newAgent: Agent) => {
    setAgents((prev) => [...prev, newAgent]);
    setShowCreateModal(false);
  };

  const handleStartChat = (agentId: string) => {
    router.push(`/chat/${agentId}`);
  };

  const handleEditAgent = (agentId: string) => {
    router.push(`/agents/${agentId}/edit`);
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm("Are you sure you want to delete this agent?")) return;

    try {
      await AgentService.deleteAgent(agentId);
      setAgents((prev) => prev.filter((agent) => agent.id !== agentId));
    } catch (error) {
      console.error("Failed to delete agent:", error);
      alert("Failed to delete agent. Please try again.");
    }
  };

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
    setShowAgentModal(true);
  };

  const handleCloseModal = () => {
    setSelectedAgent(null);
    setShowAgentModal(false);
  };

  const getAgentTypeStats = () => {
    const stats = {
      total: agents?.length,
      standard: agents.filter((a) => !a.agent_type).length,
      react: agents.filter((a) => a.agent_type === "react").length,
      sequential: agents.filter((a) => a.agent_type === "sequential").length,
      parallel: agents.filter((a) => a.agent_type === "parallel").length,
    };
    return stats;
  };

  const stats = getAgentTypeStats();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
      {/* Professional Header */}
      <header className="bg-white/90 backdrop-blur-xl shadow-sm border-b border-blue-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-sky-600 rounded-lg flex items-center justify-center shadow-md">
                <FaRobot className="text-white text-lg" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">AI Agents</h1>
                <p className="text-sm text-gray-500">
                  {filteredAgents.length} agents available
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                  showFilters
                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <FaFilter className="text-sm" />
                <span>Filters</span>
              </button>

              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-blue-500 to-sky-600 hover:from-blue-600 hover:to-sky-700 text-white px-6 py-2 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 flex items-center space-x-2"
              >
                <FaPlus className="text-sm" />
                <span>Create Agent</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
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

        {/* Filter Panel */}
        {showFilters && (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 mb-6 border border-blue-100">
            <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search agents..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/70"
                  />
                </div>
              </div>

              {/* Type Filter */}
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">
                  Type:
                </label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/70"
                >
                  <option value="all">All Types</option>
                  <option value="standard">Standard</option>
                  <option value="react">ReAct</option>
                  <option value="sequential">Sequential</option>
                  <option value="parallel">Parallel</option>
                </select>
              </div>

              {/* Sort */}
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">
                  Sort:
                </label>
                <select
                  value={sortBy}
                  onChange={(e) =>
                    setSortBy(
                      e.target.value as "name" | "created_at" | "usage_count"
                    )
                  }
                  className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/70"
                >
                  <option value="name">Name</option>
                  <option value="created_at">Created Date</option>
                  <option value="usage_count">Usage Count</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Agent Cards Grid */}

        {(filteredAgents?.length || 0) === 0 ? (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-12 text-center border border-blue-100">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-sky-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <FaRobot className="text-white text-2xl" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              {agents?.length === 0 ? "No agents yet" : "No agents found"}
            </h3>
            <p className="text-gray-600 mb-6">
              {agents?.length === 0
                ? "Create your first agent to get started"
                : "Try adjusting your search or filters"}
            </p>
            {agents?.length === 0 && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-blue-500 to-sky-600 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-sky-700 transition-all duration-200 font-medium shadow-md"
              >
                <FaPlus className="mr-2" />
                Create Agent
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {(filteredAgents || []).map((agent) => (
              <div
                key={agent.id}
                onClick={() => handleAgentClick(agent)}
                className="bg-white/80 backdrop-blur-sm rounded-xl shadow-md border border-blue-100 hover:shadow-lg transition-all duration-200 cursor-pointer group hover:border-blue-200"
              >
                <div className="p-4">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-sky-600 rounded-lg flex items-center justify-center">
                        <FaRobot className="text-white text-sm" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800 text-sm group-hover:text-blue-600 transition-colors truncate">
                          {agent.name}
                        </h3>
                        {agent.agent_type && (
                          <span
                            className={`text-xs px-1.5 py-0.5 rounded ${
                              agent.agent_type === "react"
                                ? "bg-purple-100 text-purple-600"
                                : agent.agent_type === "sequential"
                                ? "bg-green-100 text-green-600"
                                : agent.agent_type === "parallel"
                                ? "bg-orange-100 text-orange-600"
                                : "bg-gray-100 text-gray-600"
                            }`}
                          >
                            {agent.agent_type}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-1">
                      <FaStar className="text-yellow-400 text-xs" />
                      <span className="text-xs text-gray-500">4.8</span>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-xs mb-3 line-clamp-2">
                    {agent.persona?.description ||
                      agent.description ||
                      "AI agent ready to assist"}
                  </p>

                  {/* Tools */}
                  {agent.tools && agent.tools.length > 0 && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-500">
                          Tools
                        </span>
                        <span className="text-xs text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                          {agent.tools.length}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {agent.tools.slice(0, 4).map((tool, index) => {
                          const IconComponent = getToolIcon(tool);
                          return (
                            <div
                              key={index}
                              className="flex items-center bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded text-xs"
                              title={tool}
                            >
                              <IconComponent className="text-xs mr-1" />
                              <span className="truncate max-w-16">{tool}</span>
                            </div>
                          );
                        })}
                        {agent.tools.length > 4 && (
                          <span className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                            +{agent.tools.length - 4}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div className="flex items-center space-x-1">
                      <FaClock className="text-gray-400 text-xs" />
                      <span className="text-xs text-gray-500">
                        {new Date(agent.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditAgent(agent.id);
                        }}
                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Edit agent"
                      >
                        <FaEdit className="text-xs" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartChat(agent.id);
                        }}
                        className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                        title="Start chat"
                      >
                        <FaComments className="text-xs" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Agent Details Modal */}
        {showAgentModal && selectedAgent && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-sky-600 rounded-lg flex items-center justify-center">
                    <FaRobot className="text-white text-xl" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">
                      {selectedAgent.name}
                    </h2>
                    <div className="flex items-center space-x-2 mt-1">
                      {selectedAgent.agent_type && (
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            selectedAgent.agent_type === "react"
                              ? "bg-purple-100 text-purple-600"
                              : selectedAgent.agent_type === "sequential"
                              ? "bg-green-100 text-green-600"
                              : selectedAgent.agent_type === "parallel"
                              ? "bg-orange-100 text-orange-600"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {selectedAgent.agent_type}
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        v{selectedAgent.version || "1.0"}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleCloseModal}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <FaTimes className="text-xl" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6">
                {/* Description */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Description
                  </h3>
                  <p className="text-gray-600">
                    {selectedAgent.persona?.description ||
                      selectedAgent.description ||
                      "No description available"}
                  </p>
                </div>

                {/* Tools */}
                {selectedAgent.tools && selectedAgent.tools.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">
                      Tools ({selectedAgent.tools.length})
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                      {selectedAgent.tools.map((tool, index) => {
                        const IconComponent = getToolIcon(tool);
                        return (
                          <div
                            key={index}
                            className="flex items-center space-x-2 bg-blue-50 text-blue-700 px-3 py-2 rounded-lg"
                          >
                            <IconComponent className="text-sm" />
                            <span className="text-sm font-medium">{tool}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Expertise */}
                {selectedAgent.persona?.expertise &&
                  selectedAgent.persona.expertise.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-semibold text-gray-700 mb-3">
                        Expertise
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgent.persona.expertise.map((skill, index) => (
                          <span
                            key={index}
                            className="bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Stats */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    Statistics
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-gray-800">
                        {selectedAgent.usage_count || 0}
                      </div>
                      <div className="text-xs text-gray-500">Uses</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-gray-800">
                        {selectedAgent.tools?.length || 0}
                      </div>
                      <div className="text-xs text-gray-500">Tools</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-gray-800">4.8</div>
                      <div className="text-xs text-gray-500">Rating</div>
                    </div>
                  </div>
                </div>

                {/* Creation Date */}
                <div className="text-xs text-gray-500 mb-6">
                  Created on{" "}
                  {new Date(selectedAgent.created_at).toLocaleDateString()}
                </div>
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
                <button
                  onClick={() => {
                    handleCloseModal();
                    handleEditAgent(selectedAgent.id);
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-blue-600 transition-colors flex items-center space-x-2"
                >
                  <FaEdit className="text-sm" />
                  <span>Edit</span>
                </button>
                <button
                  onClick={() => {
                    handleCloseModal();
                    handleStartChat(selectedAgent.id);
                  }}
                  className="bg-gradient-to-r from-blue-500 to-sky-600 hover:from-blue-600 hover:to-sky-700 text-white px-6 py-2 rounded-lg font-medium shadow-md transition-all duration-200 flex items-center space-x-2"
                >
                  <FaComments className="text-sm" />
                  <span>Start Chat</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Create Agent Modal */}
        {showCreateModal && (
          <CreateAgentModal
            onClose={() => setShowCreateModal(false)}
            onAgentCreated={handleAgentCreated}
          />
        )}
      </main>
    </div>
  );
}
