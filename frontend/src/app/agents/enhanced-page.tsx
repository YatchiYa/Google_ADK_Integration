"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { Agent } from "@/types/agent.types";
import { AgentService } from "@/services/agent.service";
import {
  FaRobot,
  FaPlus,
  FaSearch,
  FaFilter,
  FaSync,
  FaEdit,
  FaTrash,
  FaComments,
  FaStar,
  FaTools,
  FaClock,
  FaUsers,
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
  FaWeebly,
  FaChevronDown,
  FaChevronUp,
  FaBrain,
  FaCogs,
  FaLightbulb,
  FaTimes,
} from "react-icons/fa";

export default function EnhancedAgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [sortBy, setSortBy] = useState<"name" | "created" | "tools">("name");
  const [showFilters, setShowFilters] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Tool icon mapping
  const getToolIcon = (toolName: string) => {
    const toolLower = toolName.toLowerCase();
    if (toolLower.includes("google") || toolLower.includes("search")) return FaGoogle;
    if (toolLower.includes("database") || toolLower.includes("sql")) return FaDatabase;
    if (toolLower.includes("code") || toolLower.includes("programming")) return FaCode;
    if (toolLower.includes("calculator") || toolLower.includes("math")) return FaCalculator;
    if (toolLower.includes("file") || toolLower.includes("document")) return FaFileAlt;
    if (toolLower.includes("image") || toolLower.includes("photo")) return FaImage;
    if (toolLower.includes("music") || toolLower.includes("audio")) return FaMusic;
    if (toolLower.includes("video")) return FaVideo;
    if (toolLower.includes("web") || toolLower.includes("url")) return FaGlobe;
    if (toolLower.includes("shop") || toolLower.includes("product")) return FaShoppingCart;
    if (toolLower.includes("email") || toolLower.includes("mail")) return FaEnvelope;
    if (toolLower.includes("calendar") || toolLower.includes("schedule")) return FaCalendar;
    if (toolLower.includes("map") || toolLower.includes("location")) return FaMapMarkerAlt;
    if (toolLower.includes("weather")) return FaWeebly;
    if (toolLower.includes("news")) return FaNewspaper;
    if (toolLower.includes("book") || toolLower.includes("read")) return FaBookOpen;
    if (toolLower.includes("language") || toolLower.includes("translate")) return FaLanguage;
    if (toolLower.includes("chart") || toolLower.includes("analytics")) return FaChartBar;
    if (toolLower.includes("design") || toolLower.includes("creative")) return FaPalette;
    if (toolLower.includes("game")) return FaGamepad;
    return FaRobot;
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
      setAgents(Array.isArray(agentsData) ? agentsData : []);
    } catch (error) {
      console.error("Failed to load agents:", error);
      setError(error instanceof Error ? error.message : "Failed to load agents");
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

    if (searchTerm) {
      filtered = filtered.filter(
        (agent) =>
          agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          agent.persona?.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          agent.persona?.expertise?.some((skill) =>
            skill.toLowerCase().includes(searchTerm.toLowerCase())
          )
      );
    }

    if (filterType !== "all") {
      filtered = filtered.filter((agent) => agent.agent_type === filterType);
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case "created":
          return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
        case "tools":
          return (b.tools?.length || 0) - (a.tools?.length || 0);
        case "name":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    setFilteredAgents(filtered);
  };

  const handleAgentClick = (agent: Agent) => {
    setExpandedAgent(expandedAgent === agent.id ? null : agent.id);
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm("Are you sure you want to delete this agent?")) return;

    try {
      await AgentService.deleteAgent(agentId);
      await loadAgents();
    } catch (error) {
      console.error("Failed to delete agent:", error);
      setError("Failed to delete agent. Please try again.");
    }
  };

  const getAgentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      react: "bg-blue-50 text-blue-700 border-blue-200",
      sequential: "bg-green-50 text-green-700 border-green-200",
      parallel: "bg-purple-50 text-purple-700 border-purple-200",
    };
    return colors[type] || "bg-gray-50 text-gray-700 border-gray-200";
  };

  const getAgentTypeIcon = (type: string) => {
    const icons: Record<string, any> = {
      react: FaBrain,
      sequential: FaCogs,
      parallel: FaLightbulb,
    };
    return icons[type] || FaRobot;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-pink-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading AI Agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-pink-100">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 text-white">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl mb-6">
              <FaRobot className="text-3xl text-white" />
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white to-purple-100 bg-clip-text text-transparent">
              AI Agents Hub
            </h1>
            <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
              Manage and deploy intelligent AI agents with advanced capabilities and tool integrations
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>{filteredAgents.length} Active Agents</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>{agents.reduce((acc, agent) => acc + (agent.tools?.length || 0), 0)} Total Tools</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-pink-400 rounded-full"></div>
                <span>Real-time Management</span>
              </div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-col lg:flex-row gap-4 items-center">
              <div className="flex-1 relative">
                <FaSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search agents by name, description, or expertise..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 bg-white/90 backdrop-blur-sm border border-white/20 rounded-xl focus:ring-2 focus:ring-white/50 focus:border-transparent text-gray-800 placeholder-gray-500 text-lg"
                />
              </div>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-6 py-4 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2 ${
                  showFilters
                    ? "bg-white/20 text-white border border-white/30"
                    : "bg-white/10 text-white/80 hover:bg-white/20"
                }`}
              >
                <FaFilter />
                <span>Filters</span>
              </button>
              <button
                onClick={() => router.push("/agents/create")}
                className="bg-white/20 hover:bg-white/30 text-white px-6 py-4 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2 border border-white/30"
              >
                <FaPlus />
                <span>New Agent</span>
              </button>
              <button
                onClick={loadAgents}
                className="bg-white/20 hover:bg-white/30 text-white px-6 py-4 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2 border border-white/30"
              >
                <FaSync />
                <span>Refresh</span>
              </button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-white/80 mb-2">Agent Type</label>
                    <select
                      value={filterType}
                      onChange={(e) => setFilterType(e.target.value)}
                      className="w-full px-4 py-3 bg-white/90 border border-white/20 rounded-lg focus:ring-2 focus:ring-white/50 text-gray-800"
                    >
                      <option value="all">All Types</option>
                      <option value="react">ReAct Agents</option>
                      <option value="sequential">Sequential Agents</option>
                      <option value="parallel">Parallel Agents</option>
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-white/80 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as "name" | "created" | "tools")}
                      className="w-full px-4 py-3 bg-white/90 border border-white/20 rounded-lg focus:ring-2 focus:ring-white/50 text-gray-800"
                    >
                      <option value="name">Name</option>
                      <option value="created">Created Date</option>
                      <option value="tools">Tool Count</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <p className="text-red-700 font-medium">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800 transition-colors"
              >
                <FaTimes />
              </button>
            </div>
          </div>
        )}

        {/* Agents Grid */}
        {filteredAgents.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-16 text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaRobot className="text-white text-3xl" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-4">No agents found</h3>
            <p className="text-gray-600 mb-8">Create your first AI agent or adjust your search criteria</p>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => router.push("/agents/create")}
                className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-8 py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-200"
              >
                Create Agent
              </button>
              <button
                onClick={() => {
                  setSearchTerm("");
                  setFilterType("all");
                }}
                className="bg-gray-100 text-gray-700 px-8 py-3 rounded-xl font-medium hover:bg-gray-200 transition-all duration-200"
              >
                Clear Filters
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Agents Grid - 5 per row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {filteredAgents.map((agent) => (
                <div key={agent.id} className="space-y-4">
                  {/* Agent Card */}
                  <div
                    onClick={() => handleAgentClick(agent)}
                    className="bg-white rounded-2xl shadow-md border border-gray-100 hover:shadow-xl transition-all duration-300 cursor-pointer group hover:scale-105"
                  >
                    <div className="p-6">
                      {/* Agent Icon & Header */}
                      <div className="flex flex-col items-center text-center mb-4">
                        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300">
                          {React.createElement(getAgentTypeIcon(agent.agent_type), {
                            className: "text-white text-2xl",
                          })}
                        </div>
                        <h3 className="font-bold text-gray-800 text-lg group-hover:text-purple-600 transition-colors leading-tight">
                          {agent.name}
                        </h3>
                        <span className={`text-xs px-3 py-1 rounded-full border mt-2 ${getAgentTypeColor(agent.agent_type)}`}>
                          {agent.agent_type?.toUpperCase() || "AGENT"}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-gray-600 text-sm mb-4 line-clamp-3 leading-relaxed">
                        {agent.persona?.description || "An intelligent AI agent ready to assist with various tasks."}
                      </p>

                      {/* Tools Preview */}
                      {agent.tools && agent.tools.length > 0 && (
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-gray-500">Tools</span>
                            <span className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded">
                              {agent.tools.length}
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {agent.tools.slice(0, 3).map((tool, index) => (
                              <div
                                key={index}
                                className="w-6 h-6 bg-gradient-to-br from-purple-400 to-pink-500 rounded-lg flex items-center justify-center"
                              >
                                {React.createElement(getToolIcon(tool), {
                                  className: "text-white text-xs",
                                })}
                              </div>
                            ))}
                            {agent.tools.length > 3 && (
                              <div className="w-6 h-6 bg-gray-200 rounded-lg flex items-center justify-center">
                                <span className="text-xs text-gray-600">+{agent.tools.length - 3}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Stats */}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                        <div className="flex items-center space-x-1">
                          <FaStar className="text-yellow-400" />
                          <span>4.8</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <FaTools />
                          <span>{agent.tools?.length || 0}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <FaClock />
                          <span>{new Date(agent.created_at || Date.now()).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {/* Expand Indicator */}
                      <div className="flex items-center justify-center pt-2 border-t border-gray-100">
                        {expandedAgent === agent.id ? (
                          <FaChevronUp className="text-purple-500 group-hover:text-purple-600" />
                        ) : (
                          <FaChevronDown className="text-gray-400 group-hover:text-purple-500" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details Section */}
                  {expandedAgent === agent.id && (
                    <div className="bg-white rounded-2xl shadow-lg border border-purple-200 overflow-hidden animate-fadeIn">
                      <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 border-b border-purple-100">
                        <div className="flex items-center space-x-4 mb-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                            {React.createElement(getAgentTypeIcon(agent.agent_type), {
                              className: "text-white text-xl",
                            })}
                          </div>
                          <div>
                            <h4 className="text-xl font-bold text-gray-800">{agent.name}</h4>
                            <span className={`text-sm px-3 py-1 rounded-full border ${getAgentTypeColor(agent.agent_type)}`}>
                              {agent.agent_type?.toUpperCase() || "AGENT"}
                            </span>
                          </div>
                        </div>

                        {/* Detailed Description */}
                        <div className="mb-6">
                          <h5 className="font-semibold text-gray-700 mb-2 flex items-center">
                            <FaBrain className="mr-2" />
                            Description
                          </h5>
                          <p className="text-gray-600 leading-relaxed">
                            {agent.persona?.description || "An intelligent AI agent designed to assist with various tasks and provide expert-level support across multiple domains."}
                          </p>
                        </div>

                        {/* Expertise */}
                        {agent.persona?.expertise && agent.persona.expertise.length > 0 && (
                          <div className="mb-6">
                            <h5 className="font-semibold text-gray-700 mb-3 flex items-center">
                              <FaLightbulb className="mr-2" />
                              Expertise
                            </h5>
                            <div className="flex flex-wrap gap-2">
                              {agent.persona.expertise.map((skill, index) => (
                                <span
                                  key={index}
                                  className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm border border-purple-200"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Tools Grid */}
                        {agent.tools && agent.tools.length > 0 && (
                          <div className="mb-6">
                            <h5 className="font-semibold text-gray-700 mb-3 flex items-center">
                              <FaTools className="mr-2" />
                              Integrated Tools ({agent.tools.length})
                            </h5>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                              {agent.tools.map((tool, index) => (
                                <div
                                  key={index}
                                  className="flex items-center space-x-2 p-3 bg-white rounded-lg border border-purple-100 hover:border-purple-200 transition-colors"
                                >
                                  <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-500 rounded-lg flex items-center justify-center">
                                    {React.createElement(getToolIcon(tool), {
                                      className: "text-white text-sm",
                                    })}
                                  </div>
                                  <span className="text-sm font-medium text-gray-700 truncate">
                                    {tool.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Statistics */}
                        <div className="mb-6">
                          <h5 className="font-semibold text-gray-700 mb-3 flex items-center">
                            <FaChartBar className="mr-2" />
                            Statistics
                          </h5>
                          <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-4 bg-white rounded-xl border border-purple-100">
                              <div className="text-2xl font-bold text-purple-600">{agent.tools?.length || 0}</div>
                              <div className="text-sm text-gray-500">Tools</div>
                            </div>
                            <div className="text-center p-4 bg-white rounded-xl border border-pink-100">
                              <div className="text-2xl font-bold text-pink-600">4.8</div>
                              <div className="text-sm text-gray-500">Rating</div>
                            </div>
                            <div className="text-center p-4 bg-white rounded-xl border border-indigo-100">
                              <div className="text-2xl font-bold text-indigo-600">
                                {Math.floor(Math.random() * 50) + 10}
                              </div>
                              <div className="text-sm text-gray-500">Uses</div>
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-wrap gap-3">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/chat/${agent.id}`);
                            }}
                            className="flex-1 bg-gradient-to-r from-purple-500 to-pink-600 text-white px-4 py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-200 flex items-center justify-center space-x-2"
                          >
                            <FaComments />
                            <span>Start Chat</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/agents/edit/${agent.id}`);
                            }}
                            className="px-4 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-all duration-200 flex items-center space-x-2"
                          >
                            <FaEdit />
                            <span>Edit</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteAgent(agent.id);
                            }}
                            className="px-4 py-3 bg-red-100 text-red-700 rounded-xl font-medium hover:bg-red-200 transition-all duration-200 flex items-center space-x-2"
                          >
                            <FaTrash />
                            <span>Delete</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
