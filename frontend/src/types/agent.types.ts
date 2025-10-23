export interface AgentPersona {
  name: string;
  description: string;
  personality: string;
  expertise: string[];
  communication_style: string;
  language?: string;
  custom_instructions?: string;
  examples?: Array<{ input: string; output: string }>;
}

export interface AgentConfig {
  model: string;
  temperature: number;
  max_output_tokens: number;
  top_p?: number;
  top_k?: number;
  timeout_seconds?: number;
  retry_attempts?: number;
}

export interface Agent {
  id: string;
  agent_id?: string; // For API compatibility
  name: string;
  description?: string;
  persona: AgentPersona;
  config?: AgentConfig;
  tools: string[];
  agent_type?: 'react' | 'sequential' | 'parallel' | null;
  planner?: string;
  sub_agents?: string[];
  created_at: string;
  last_used?: string;
  usage_count: number;
  is_active: boolean;
  version?: string;
  metadata?: Record<string, any>;
}

export interface CreateAgentRequest {
  name: string;
  persona: AgentPersona;
  config?: AgentConfig;
  tools?: string[];
  agent_id?: string;
  planner?: string;
  agent_type?: string;
  sub_agents?: string[];
}

export interface AttachToolsRequest {
  tool_names: string[];
}

export interface DetachToolsRequest {
  tool_names: string[];
}

export interface AgentToolsResponse {
  success: boolean;
  agent_id: string;
  tools: string[];
  message: string;
}

export interface BaseResponse {
  success: boolean;
  message: string;
  timestamp?: string;
}

export interface AgentListResponse extends BaseResponse {
  data: Agent[];
  total: number;
  offset: number;
  limit: number;
}
