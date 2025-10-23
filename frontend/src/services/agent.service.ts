import { AuthService } from './auth.service';
import { 
  Agent, 
  CreateAgentRequest, 
  AgentListResponse, 
  BaseResponse,
  AttachToolsRequest,
  DetachToolsRequest,
  AgentToolsResponse
} from '@/types/agent.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class AgentServiceClass {
  async getAgents(activeOnly: boolean = true, limit: number = 50, offset: number = 0): Promise<Agent[]> {
    const params = new URLSearchParams({
      active_only: activeOnly.toString(),
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/agents/?${params}`, {
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agents');
    }

    const data = await response.json();
    
    // Handle different response structures
    const agents = data.agents || data.data || [];
    
    // Transform agent_id to id if needed
    return agents.map((agent: any) => ({
      ...agent,
      id: agent.id || agent.agent_id,
      description: agent.description || agent.persona?.description || ''
    }));
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}`, {
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agent');
    }

    const data = await response.json();
    const agent = data.agent || data.data || data;
    
    // Transform agent_id to id if needed
    return {
      ...agent,
      id: agent.id || agent.agent_id,
      description: agent.description || agent.persona?.description || ''
    };
  }

  async createAgent(agentData: CreateAgentRequest): Promise<Agent> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(agentData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create agent');
    }

    const result: BaseResponse = await response.json();
    
    // Extract agent ID from message
    const agentIdMatch = result.message.match(/agent_([a-f0-9]+)/);
    if (!agentIdMatch) {
      throw new Error('Failed to extract agent ID from response');
    }

    // Fetch the created agent
    return this.getAgent(agentIdMatch[0]);
  }

  async updateAgent(agentId: string, updates: Partial<CreateAgentRequest>): Promise<Agent> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}`, {
      method: 'PUT',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error('Failed to update agent');
    }

    return this.getAgent(agentId);
  }

  async deleteAgent(agentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}`, {
      method: 'DELETE',
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete agent');
    }
  }

  async attachTools(agentId: string, toolNames: string[]): Promise<void> {
    const request: AttachToolsRequest = { tool_names: toolNames };
    
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/tools/attach`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to attach tools');
    }
  }

  async detachTools(agentId: string, toolNames: string[]): Promise<void> {
    const request: DetachToolsRequest = { tool_names: toolNames };
    
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/tools/detach`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to detach tools');
    }
  }

  async getAgentTools(agentId: string): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/tools`, {
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agent tools');
    }

    const data: AgentToolsResponse = await response.json();
    return data.tools;
  }

  async getAvailableTools(): Promise<string[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/tools/`, {
        headers: AuthService.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch available tools');
      }

      const data = await response.json();
      return data.tools?.map((tool: any) => tool.name) || [];
    } catch (error) {
      console.error('Failed to fetch tools from API, using fallback:', error);
      // Fallback to static list
      return [
        'google_search_agent',
        'custom_calculator',
        'text_analyzer',
        'product_hunt_search',
        'load_memory',
        'save_memory',
        'search_memory',
        'web_scraper',
        'email_sender',
        'file_reader',
        'code_executor',
        'image_generator'
      ];
    }
  }

  async updateAgentConfig(agentId: string, config: {
    agent_type?: string;
    planner?: string;
    tools?: string[];
  }): Promise<Agent> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/config`, {
      method: 'PUT',
      headers: AuthService.getAuthHeaders(),
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update agent configuration');
    }

    return this.getAgent(agentId);
  }

  async stopStreaming(agentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/stop`, {
      method: 'POST',
      headers: AuthService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to stop streaming');
    }
  }
}

export const AgentService = new AgentServiceClass();
