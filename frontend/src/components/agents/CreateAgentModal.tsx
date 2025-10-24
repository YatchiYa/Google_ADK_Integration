"use client";

import type React from "react";

import { useState, useEffect } from "react";
import type {
  Agent,
  CreateAgentRequest,
  AgentPersona,
} from "@/types/agent.types";
import { AgentService } from "@/services/agent.service";
import { FaTimes, FaRobot, FaSpinner, FaCheckCircle } from "react-icons/fa";

interface CreateAgentModalProps {
  onClose: () => void;
  onAgentCreated: (agent: Agent) => void;
}

export default function CreateAgentModal({
  onClose,
  onAgentCreated,
}: CreateAgentModalProps) {
  const [loading, setLoading] = useState(false);
  const [availableTools, setAvailableTools] = useState<string[]>([]);
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);

  const [formData, setFormData] = useState<CreateAgentRequest>({
    name: "",
    persona: {
      name: "",
      description: "",
      personality: "",
      expertise: [],
      communication_style: "professional",
      language: "en",
      custom_instructions: "",
      examples: [],
    },
    config: {
      model: "gemini-2.0-flash",
      temperature: 0.7,
      max_output_tokens: 2048,
      top_p: 0.9,
      top_k: 40,
      timeout_seconds: 30,
      retry_attempts: 3,
    },
    tools: [],
    agent_type: "regular",
    planner: "",
    sub_agents: [],
  });

  useEffect(() => {
    loadAvailableResources();
  }, []);

  const loadAvailableResources = async () => {
    try {
      const [tools, agents] = await Promise.all([
        AgentService.getAvailableTools(),
        AgentService.getAgents(),
      ]);
      setAvailableTools(tools);
      setAvailableAgents(agents);
    } catch (error) {
      console.error("Failed to load resources:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const cleanedData: CreateAgentRequest = {
        ...formData,
        agent_type: formData.agent_type || undefined,
        planner: formData.planner || undefined,
        tools: formData.tools?.filter((tool) => tool.trim() !== ""),
        sub_agents: formData.sub_agents?.filter((agent) => agent.trim() !== ""),
        persona: {
          ...formData.persona,
          expertise: formData.persona.expertise.filter(
            (skill) => skill.trim() !== ""
          ),
        },
      };

      const newAgent = await AgentService.createAgent(cleanedData);
      onAgentCreated(newAgent);
    } catch (error) {
      console.error("Failed to create agent:", error);
      alert("Failed to create agent. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handlePersonaChange = (field: keyof AgentPersona, value: any) => {
    setFormData((prev) => ({
      ...prev,
      persona: {
        ...prev.persona,
        [field]: value,
      },
    }));
  };

  const handleExpertiseChange = (value: string) => {
    const skills = value.split(",").map((skill) => skill.trim());
    handlePersonaChange("expertise", skills);
  };

  const handleToolToggle = (tool: string) => {
    setFormData((prev) => ({
      ...prev,
      tools: prev.tools?.includes(tool)
        ? prev.tools.filter((t) => t !== tool)
        : [...(prev.tools || []), tool],
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-blue-100">
        {/* Header */}
        <div className="flex items-center justify-between p-8 border-b border-blue-100 bg-gradient-to-r from-blue-50 to-cyan-50">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <FaRobot className="text-white text-xl" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Create New Agent
              </h2>
              <p className="text-sm text-gray-600 mt-0.5">
                Build your intelligent AI assistant
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-2 hover:bg-white rounded-xl"
          >
            <FaTimes className="text-xl" />
          </button>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="p-8 space-y-6 overflow-y-auto max-h-[calc(90vh-180px)]"
        >
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Agent Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="e.g., Research Assistant"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Persona Name
              </label>
              <input
                type="text"
                value={formData.persona.name}
                onChange={(e) => handlePersonaChange("name", e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="e.g., Research Expert"
              />
            </div>
          </div>

          {/* Agent Type */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Agent Type
              </label>
              <select
                value={formData.agent_type}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    agent_type: e.target.value,
                  }))
                }
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              >
                <option value="">Standard Agent</option>
                <option value="PlanReActPlanner">ReAct Planner Agent</option>
                <option value="BuiltInPlanner">Built-in Planner Agent</option>
                <option value="BuiltInPlannerAdvanced">
                  Advanced Built-in Planner Agent
                </option>
                <option value="SequentialAgent">Sequential Agent</option>
                <option value="ParallelAgent">Parallel Agent</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Communication Style
              </label>
              <select
                value={formData.persona.communication_style}
                onChange={(e) =>
                  handlePersonaChange("communication_style", e.target.value)
                }
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              >
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="academic">Academic</option>
                <option value="casual">Casual</option>
                <option value="concise">Concise</option>
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              required
              rows={3}
              value={formData.persona.description}
              onChange={(e) =>
                handlePersonaChange("description", e.target.value)
              }
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              placeholder="Describe the agent's purpose and capabilities..."
            />
          </div>

          {/* Personality & Expertise */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Personality
              </label>
              <input
                type="text"
                value={formData.persona.personality}
                onChange={(e) =>
                  handlePersonaChange("personality", e.target.value)
                }
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="e.g., analytical and thorough"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Expertise (comma-separated)
              </label>
              <input
                type="text"
                value={formData.persona.expertise.join(", ")}
                onChange={(e) => handleExpertiseChange(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="e.g., research, data analysis, web search"
              />
            </div>
          </div>

          {/* Tools Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Available Tools
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-h-48 overflow-y-auto border-2 border-gray-200 rounded-xl p-4 bg-gray-50">
              {availableTools.map((tool) => (
                <label
                  key={tool}
                  className="flex items-center gap-2 cursor-pointer hover:bg-white p-3 rounded-lg transition-all duration-200 border border-transparent hover:border-blue-200"
                >
                  <input
                    type="checkbox"
                    checked={formData.tools?.includes(tool) || false}
                    onChange={() => handleToolToggle(tool)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    {tool}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Agent as Tool Selection */}
          {(availableAgents?.length || 0) > 0 && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Use Other Agents as Tools
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto border-2 border-gray-200 rounded-xl p-4 bg-gray-50">
                {(availableAgents || []).map((agent) => (
                  <label
                    key={agent.id}
                    className="flex items-center gap-2 cursor-pointer hover:bg-white p-3 rounded-lg transition-all duration-200 border border-transparent hover:border-purple-200"
                  >
                    <input
                      type="checkbox"
                      checked={
                        formData.tools?.includes(`agent:${agent.id}`) || false
                      }
                      onChange={() => handleToolToggle(`agent:${agent.id}`)}
                      className="w-4 h-4 text-purple-600 focus:ring-purple-500 rounded"
                    />
                    <span className="text-sm flex items-center gap-1.5 font-medium text-gray-700">
                      <FaRobot className="text-purple-500" />
                      {agent.name}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Custom Instructions */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              rows={3}
              value={formData.persona.custom_instructions}
              onChange={(e) =>
                handlePersonaChange("custom_instructions", e.target.value)
              }
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              placeholder="Additional instructions for the agent..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-all duration-200 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 transition-all duration-200 flex items-center gap-2 font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-105 disabled:hover:scale-100"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <FaCheckCircle />
                  Create Agent
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
