"use client";

import React, { useState, useEffect } from "react";
import type { Agent } from "@/types/agent.types";
import { AgentService } from "@/services/agent.service";
import {
  FaTools,
  FaRobot,
  FaSearch,
  FaFilter,
  FaSync,
  FaCheck,
  FaTimes,
  FaStar,
  FaUsers,
  FaLink,
  FaUnlink,
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
  FaDownload,
  FaWeebly,
  FaChevronDown,
  FaChevronUp,
  FaBookReader,
  FaCogs,
} from "react-icons/fa";

interface ToolInfo {
  name: string;
  description: string;
  category: string;
  usedByAgents: string[];
  popularity?: number;
  rating?: number;
}

export default function EnhancedToolsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [availableTools, setAvailableTools] = useState<string[]>([]);
  const [toolsInfo, setToolsInfo] = useState<ToolInfo[]>([]);
  const [filteredTools, setFilteredTools] = useState<ToolInfo[]>([]);
  const [expandedTool, setExpandedTool] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [sortBy, setSortBy] = useState<"name" | "popularity" | "agents">(
    "name"
  );
  const [showFilters, setShowFilters] = useState(false);
  const [processingTools, setProcessingTools] = useState<Set<string>>(
    new Set()
  );
  const [error, setError] = useState<string | null>(null);

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
    return FaTools;
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterAndSortTools();
  }, [toolsInfo, searchTerm, selectedCategory, sortBy]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [agentsData, toolsData] = await Promise.all([
        AgentService.getAgents(),
        AgentService.getAvailableTools(),
      ]);

      setAgents(Array.isArray(agentsData) ? agentsData : []);
      setAvailableTools(Array.isArray(toolsData) ? toolsData : []);

      const toolsWithInfo: ToolInfo[] = (toolsData || []).map((tool) => ({
        name: tool,
        description: getToolDescription(tool),
        category: getToolCategory(tool),
        usedByAgents: (agentsData || [])
          .filter((agent) => agent?.tools?.includes(tool))
          .map((agent) => agent.name),
        popularity: Math.floor(Math.random() * 100) + 1,
        rating: 4.2 + Math.random() * 0.6,
      }));

      setToolsInfo(toolsWithInfo);
    } catch (error) {
      console.error("Failed to load data:", error);
      setError(error instanceof Error ? error.message : "Failed to load tools");
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortTools = () => {
    let filtered = [...toolsInfo];

    if (searchTerm) {
      filtered = filtered.filter(
        (tool) =>
          tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tool.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tool.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter((tool) => tool.category === selectedCategory);
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case "popularity":
          return (b.popularity || 0) - (a.popularity || 0);
        case "agents":
          return b.usedByAgents.length - a.usedByAgents.length;
        case "name":
        default:
          return a.name.localeCompare(b.name);
      }
    });

    setFilteredTools(filtered);
  };

  const getToolDescription = (toolName: string): string => {
    const descriptions: Record<string, string> = {
      google_search:
        "Search the web using Google Search API with advanced filtering and result processing",
      custom_calculator:
        "Perform complex mathematical calculations, equations, and computational tasks",
      text_analyzer:
        "Analyze text for sentiment, themes, key insights, and linguistic patterns",
      product_hunt_search:
        "Search and discover trending products, startups, and innovations on Product Hunt",
      load_memory:
        "Load and retrieve stored memories, context, and historical information",
      save_memory:
        "Save important information to persistent memory storage for future reference",
      search_memory:
        "Search through stored memories and knowledge base with semantic understanding",
      web_scraper:
        "Extract content, data, and structured information from web pages and sites",
      email_sender:
        "Send professional emails, notifications, and automated communications",
      file_reader:
        "Read, parse, and process various file formats including documents and media",
      code_executor:
        "Execute and run code in multiple programming languages with safety controls",
      image_generator:
        "Generate high-quality images using advanced AI models and prompts",
    };
    return (
      descriptions[toolName] ||
      "A specialized tool that enhances agent capabilities with advanced functionality"
    );
  };

  const getToolCategory = (toolName: string): string => {
    const categories: Record<string, string> = {
      google_search: "Search & Discovery",
      product_hunt_search: "Search & Discovery",
      web_scraper: "Search & Discovery",
      custom_calculator: "Computation",
      code_executor: "Computation",
      text_analyzer: "Analysis",
      image_generator: "Generation",
      load_memory: "Memory",
      save_memory: "Memory",
      search_memory: "Memory",
      email_sender: "Communication",
      file_reader: "File Processing",
    };
    return categories[toolName] || "General";
  };

  const getUniqueCategories = () => {
    const categories = [...new Set(toolsInfo.map((tool) => tool.category))];
    return ["all", ...categories.sort()];
  };

  const handleToolClick = (tool: ToolInfo) => {
    setExpandedTool(expandedTool === tool.name ? null : tool.name);
  };

  const handleAttachTool = async (agentId: string, toolName: string) => {
    setProcessingTools((prev) => new Set([...prev, `${agentId}-${toolName}`]));

    try {
      await AgentService.attachTools(agentId, [toolName]);
      await loadData();
    } catch (error) {
      console.error("Failed to attach tool:", error);
      setError("Failed to attach tool. Please try again.");
    } finally {
      setProcessingTools((prev) => {
        const newSet = new Set(prev);
        newSet.delete(`${agentId}-${toolName}`);
        return newSet;
      });
    }
  };

  const handleDetachTool = async (agentId: string, toolName: string) => {
    setProcessingTools((prev) => new Set([...prev, `${agentId}-${toolName}`]));

    try {
      await AgentService.detachTools(agentId, [toolName]);
      await loadData();
    } catch (error) {
      console.error("Failed to detach tool:", error);
      setError("Failed to detach tool. Please try again.");
    } finally {
      setProcessingTools((prev) => {
        const newSet = new Set(prev);
        newSet.delete(`${agentId}-${toolName}`);
        return newSet;
      });
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Search & Discovery": "bg-blue-50 text-blue-700 border-blue-200",
      Computation: "bg-green-50 text-green-700 border-green-200",
      Analysis: "bg-purple-50 text-purple-700 border-purple-200",
      Generation: "bg-pink-50 text-pink-700 border-pink-200",
      Memory: "bg-yellow-50 text-yellow-700 border-yellow-200",
      Communication: "bg-indigo-50 text-indigo-700 border-indigo-200",
      "File Processing": "bg-gray-50 text-gray-700 border-gray-200",
      General: "bg-gray-50 text-gray-700 border-gray-200",
    };
    return colors[category] || "bg-gray-50 text-gray-700 border-gray-200";
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading AI Tools...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-white border-b border-gray-200 overflow-hidden">
        {/* Background Icons */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-10 left-10">
            <FaTools className="text-6xl text-blue-500" />
          </div>
          <div className="absolute top-20 right-20">
            <FaGoogle className="text-5xl text-green-500" />
          </div>
          <div className="absolute bottom-20 left-20">
            <FaCode className="text-4xl text-purple-500" />
          </div>
          <div className="absolute bottom-10 right-10">
            <FaDatabase className="text-5xl text-orange-500" />
          </div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <FaCogs className="text-8xl text-gray-400" />
          </div>
        </div>

        <div className="relative max-w-7xl mx-auto px-6 py-16">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-2xl mb-6">
              <FaTools className="text-2xl text-blue-600" />
            </div>
            <h1 className="text-4xl font-bold mb-4 text-gray-900">
              AI Tools Marketplace
            </h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Discover and integrate powerful AI tools to enhance your agents'
              capabilities
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>{filteredTools.length} Tools Available</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>{agents.length} Active Agents</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Real-time Integration</span>
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
                  placeholder="Search tools by name, description, or category..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800 placeholder-gray-500 text-lg"
                />
              </div>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-6 py-4 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2 ${
                  showFilters
                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <FaFilter />
                <span>Filters</span>
              </button>
              <button
                onClick={loadData}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-xl font-medium transition-all duration-200 flex items-center space-x-2"
              >
                <FaSync />
                <span>Refresh</span>
              </button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="mt-6 bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-800"
                    >
                      {getUniqueCategories().map((category) => (
                        <option key={category} value={category}>
                          {category === "all" ? "All Categories" : category}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sort By
                    </label>
                    <select
                      value={sortBy}
                      onChange={(e) =>
                        setSortBy(
                          e.target.value as "name" | "popularity" | "agents"
                        )
                      }
                      className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-800"
                    >
                      <option value="name">Name</option>
                      <option value="popularity">Popularity</option>
                      <option value="agents">Agent Usage</option>
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

        {/* Tools Grid */}
        {filteredTools.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-16 text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaTools className="text-white text-3xl" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              No tools found
            </h3>
            <p className="text-gray-600 mb-8">
              Try adjusting your search criteria or filters
            </p>
            <button
              onClick={() => {
                setSearchTerm("");
                setSelectedCategory("all");
              }}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-xl font-medium hover:shadow-lg transition-all duration-200"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Tools Grid - 4 per row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
              {filteredTools.map((tool, index) => (
                <div key={tool.name}>
                  {/* Tool Card */}
                  <div
                    onClick={() => handleToolClick(tool)}
                    className="bg-white rounded-2xl shadow-md border border-gray-100 hover:shadow-xl transition-all duration-300 cursor-pointer group hover:scale-105"
                  >
                    <div className="p-6">
                      {/* Tool Icon & Header */}
                      <div className="flex flex-col items-center text-center mb-4">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300">
                          {React.createElement(getToolIcon(tool.name), {
                            className: "text-white text-2xl",
                          })}
                        </div>
                        <h3 className="font-bold text-gray-800 text-lg group-hover:text-blue-600 transition-colors leading-tight">
                          {tool.name
                            .replace(/_/g, " ")
                            .replace(/\b\w/g, (l) => l.toUpperCase())}
                        </h3>
                        <span
                          className={`text-xs px-3 py-1 rounded-full border mt-2 ${getCategoryColor(
                            tool.category
                          )}`}
                        >
                          {tool.category}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-gray-600 text-sm mb-4 line-clamp-3 leading-relaxed">
                        {tool.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                        <div className="flex items-center space-x-1">
                          <FaStar className="text-yellow-400" />
                          <span>{tool.rating?.toFixed(1) || "4.5"}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <FaUsers />
                          <span>{tool.usedByAgents.length}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <FaDownload />
                          <span>{tool.popularity || 0}</span>
                        </div>
                      </div>

                      {/* Expand Indicator */}
                      <div className="flex items-center justify-center pt-2 border-t border-gray-100">
                        {expandedTool === tool.name ? (
                          <FaChevronUp className="text-blue-500 group-hover:text-blue-600" />
                        ) : (
                          <FaChevronDown className="text-gray-400 group-hover:text-blue-500" />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Full-Width Expanded Details Section */}
            {expandedTool &&
              (() => {
                const selectedTool = filteredTools.find(
                  (tool) => tool.name === expandedTool
                );
                if (!selectedTool) return null;

                return (
                  <div className="bg-white rounded-2xl shadow-lg border border-blue-200 overflow-hidden animate-fadeIn">
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-4">
                          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                            {React.createElement(
                              getToolIcon(selectedTool.name),
                              {
                                className: "text-white text-2xl",
                              }
                            )}
                          </div>
                          <div>
                            <h4 className="text-2xl font-bold text-gray-800">
                              {selectedTool.name
                                .replace(/_/g, " ")
                                .replace(/\b\w/g, (l) => l.toUpperCase())}
                            </h4>
                            <span
                              className={`text-sm px-3 py-1 rounded-full border ${getCategoryColor(
                                selectedTool.category
                              )}`}
                            >
                              {selectedTool.category}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => setExpandedTool(null)}
                          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          <FaTimes className="text-xl" />
                        </button>
                      </div>

                      {/* Detailed Description */}
                      <div className="mb-8">
                        <h5 className="font-semibold text-gray-700 mb-3 flex items-center text-lg">
                          <FaBookReader className="mr-2" />
                          Documentation
                        </h5>
                        <p className="text-gray-600 leading-relaxed text-base">
                          {selectedTool.description}
                        </p>
                      </div>

                      {/* Statistics Grid */}
                      <div className="grid grid-cols-3 gap-6 mb-8">
                        <div className="text-center p-6 bg-white rounded-xl border border-blue-100">
                          <div className="text-3xl font-bold text-blue-600 mb-2">
                            {selectedTool.usedByAgents.length}
                          </div>
                          <div className="text-sm text-gray-500">
                            Active Agents
                          </div>
                        </div>
                        <div className="text-center p-6 bg-white rounded-xl border border-purple-100">
                          <div className="text-3xl font-bold text-purple-600 mb-2">
                            {selectedTool.popularity || 0}
                          </div>
                          <div className="text-sm text-gray-500">Downloads</div>
                        </div>
                        <div className="text-center p-6 bg-white rounded-xl border border-yellow-100">
                          <div className="text-3xl font-bold text-yellow-600 mb-2">
                            {selectedTool.rating?.toFixed(1) || "4.5"}
                          </div>
                          <div className="text-sm text-gray-500">Rating</div>
                        </div>
                      </div>

                      {/* Agent Management */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Currently Used By */}
                        <div>
                          <h5 className="font-semibold text-gray-700 mb-4 flex items-center text-lg">
                            <FaUsers className="mr-2" />
                            Currently Used By (
                            {selectedTool.usedByAgents.length})
                          </h5>
                          {selectedTool.usedByAgents.length > 0 ? (
                            <div className="space-y-3 max-h-64 overflow-y-auto">
                              {selectedTool.usedByAgents.map(
                                (agentName, idx) => (
                                  <div
                                    key={idx}
                                    className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200"
                                  >
                                    <div className="flex items-center space-x-3">
                                      <FaRobot className="text-green-600" />
                                      <span className="font-medium text-gray-800">
                                        {agentName}
                                      </span>
                                    </div>
                                    <button
                                      onClick={() => {
                                        const agent = agents.find(
                                          (a) => a.name === agentName
                                        );
                                        if (agent)
                                          handleDetachTool(
                                            agent.id,
                                            selectedTool.name
                                          );
                                      }}
                                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                                      title="Detach from agent"
                                    >
                                      <FaUnlink />
                                    </button>
                                  </div>
                                )
                              )}
                            </div>
                          ) : (
                            <p className="text-gray-500 italic">
                              No agents currently using this tool
                            </p>
                          )}
                        </div>

                        {/* Agent Selector */}
                        <div>
                          <h5 className="font-semibold text-gray-700 mb-4 flex items-center text-lg">
                            <FaCogs className="mr-2" />
                            Attach to Agents
                          </h5>
                          <div className="space-y-3 max-h-64 overflow-y-auto">
                            {agents
                              .filter(
                                (agent) =>
                                  !agent.tools?.includes(selectedTool.name)
                              )
                              .map((agent) => {
                                const isProcessing = processingTools.has(
                                  `${agent.id}-${selectedTool.name}`
                                );
                                return (
                                  <div
                                    key={agent.id}
                                    className="flex items-center justify-between p-4 bg-gray-50 hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-200 transition-all duration-200"
                                  >
                                    <div className="flex items-center space-x-3">
                                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                        <FaRobot className="text-white" />
                                      </div>
                                      <div>
                                        <div className="font-medium text-gray-800">
                                          {agent.name}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                          {agent.tools?.length || 0} tools
                                          attached
                                        </div>
                                      </div>
                                    </div>
                                    <button
                                      onClick={() =>
                                        handleAttachTool(
                                          agent.id,
                                          selectedTool.name
                                        )
                                      }
                                      disabled={isProcessing}
                                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                        isProcessing
                                          ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                                          : "bg-blue-600 text-white hover:bg-blue-700"
                                      }`}
                                    >
                                      {isProcessing ? (
                                        <FaSync className="animate-spin" />
                                      ) : (
                                        <>
                                          <FaLink className="mr-2" />
                                          Attach
                                        </>
                                      )}
                                    </button>
                                  </div>
                                );
                              })}
                            {agents.filter(
                              (agent) =>
                                !agent.tools?.includes(selectedTool.name)
                            ).length === 0 && (
                              <p className="text-gray-500 italic">
                                All agents already have this tool attached
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
          </div>
        )}
      </main>
    </div>
  );
}
