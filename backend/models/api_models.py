"""
API Models for Google ADK FastAPI Application
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_type: str
    error_details: Optional[Dict[str, Any]] = None


# Agent Models
class AgentPersonaModel(BaseModel):
    """Agent persona configuration"""
    name: str
    description: str
    personality: str
    expertise: List[str] = []
    communication_style: str = "professional"
    language: str = "en"
    custom_instructions: str = ""
    examples: List[Dict[str, str]] = []


class AgentConfigModel(BaseModel):
    """Agent configuration parameters"""
    model: str = "gemini-2.0-flash"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=2048, ge=1, le=8192)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_attempts: int = Field(default=3, ge=1, le=10)


class CreateAgentRequest(BaseModel):
    """Request to create a new agent"""
    name: str = Field(..., min_length=1, max_length=100)
    persona: AgentPersonaModel
    config: Optional[AgentConfigModel] = None
    tools: List[str] = []
    agent_id: Optional[str] = None
    planner: Optional[str] = None
    agent_type: Optional[str] = None
    sub_agents: Optional[List[str]] = None


class AgentInfoResponse(BaseModel):
    """Agent information response"""
    agent_id: str
    name: str
    description: str
    persona: AgentPersonaModel
    config: AgentConfigModel
    tools: List[str]
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    version: str
    metadata: Dict[str, Any]


class UpdateAgentRequest(BaseModel):
    """Request to update agent"""
    persona: Optional[AgentPersonaModel] = None
    config: Optional[AgentConfigModel] = None
    tools: Optional[List[str]] = None


# Tool Models
class ToolInfoResponse(BaseModel):
    """Tool information response"""
    name: str
    description: str
    category: str
    version: str
    author: str
    registered_at: datetime
    usage_count: int
    is_enabled: bool
    metadata: Dict[str, Any]


class RegisterToolRequest(BaseModel):
    """Request to register a tool"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    category: str = "custom"
    version: str = "1.0.0"
    author: str = "user"
    dependencies: List[str] = []
    metadata: Dict[str, Any] = {}
    force_replace: bool = False


# Memory Models
class MemoryEntryModel(BaseModel):
    """Memory entry model"""
    content: str
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    importance: float = Field(default=1.0, ge=0.0, le=1.0)


class CreateMemoryRequest(BaseModel):
    """Request to create memory entry"""
    user_id: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    entry: MemoryEntryModel


class SearchMemoryRequest(BaseModel):
    """Request to search memory"""
    user_id: str
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    min_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = []
    session_id: Optional[str] = None
    agent_id: Optional[str] = None


class MemoryEntryResponse(BaseModel):
    """Memory entry response"""
    entry_id: str
    user_id: str
    session_id: Optional[str]
    agent_id: Optional[str]
    content: str
    metadata: Dict[str, Any]
    tags: List[str]
    importance: float
    relevance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime


# Team Models
class TeamType(str, Enum):
    """Team execution types"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    LOOP = "loop"


class CreateTeamRequest(BaseModel):
    """Request to create a team"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    team_type: TeamType
    agent_ids: List[str] = Field(..., min_items=2)
    coordinator_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class TeamInfoResponse(BaseModel):
    """Team information response"""
    team_id: str
    name: str
    description: str
    team_type: TeamType
    agent_ids: List[str]
    coordinator_id: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    metadata: Dict[str, Any]


# Conversation Models
class MessageRole(str, Enum):
    """Message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageModel(BaseModel):
    """Chat message model"""
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class StartConversationRequest(BaseModel):
    """Request to start a conversation"""
    user_id: str
    agent_id: str
    message: str
    session_id: Optional[str] = None
    context: Dict[str, Any] = {}


class SendMessageRequest(BaseModel):
    """Request to send a message"""
    message: str
    metadata: Dict[str, Any] = {}


class ConversationResponse(BaseModel):
    """Conversation response"""
    session_id: str
    user_id: str
    agent_id: str
    messages: List[MessageModel]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    metadata: Dict[str, Any]


# Streaming Models
class StreamingEventType(str, Enum):
    """Streaming event types"""
    START = "start"
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    THINKING = "thinking"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"


class StreamingEventModel(BaseModel):
    """Streaming event model"""
    type: StreamingEventType
    content: str = ""
    metadata: Dict[str, Any] = {}
    timestamp: float
    session_id: Optional[str] = None
    agent_id: Optional[str] = None


class StartStreamingRequest(BaseModel):
    """Request to start streaming"""
    user_id: str
    agent_id: str
    message: str
    session_id: Optional[str] = None


# Statistics Models
class AgentStatsResponse(BaseModel):
    """Agent statistics response"""
    total_agents: int
    active_agents: int
    inactive_agents: int
    most_used_agents: List[tuple]
    model_distribution: Dict[str, int]
    total_usage: int


class ToolStatsResponse(BaseModel):
    """Tool statistics response"""
    total_tools: int
    enabled_tools: int
    disabled_tools: int
    categories: int
    category_breakdown: Dict[str, int]
    most_used_tools: List[tuple]
    total_usage: int


class MemoryStatsResponse(BaseModel):
    """Memory statistics response"""
    total_entries: int
    entries_by_user: Dict[str, int]
    entries_by_agent: Dict[str, int]
    storage_size_mb: float
    average_importance: float


class StreamingStatsResponse(BaseModel):
    """Streaming statistics response"""
    active_sessions: int
    total_sessions: int
    total_events_sent: int
    total_tokens_processed: int
    update_interval_ms: float
    batch_size: int
    buffer_timeout_ms: float


# List Response Models
class AgentListResponse(BaseResponse):
    """Agent list response"""
    agents: List[AgentInfoResponse]
    total: int


class ToolListResponse(BaseResponse):
    """Tool list response"""
    tools: List[ToolInfoResponse]
    total: int


class MemoryListResponse(BaseResponse):
    """Memory list response"""
    entries: List[MemoryEntryResponse]
    total: int


class TeamListResponse(BaseResponse):
    """Team list response"""
    teams: List[TeamInfoResponse]
    total: int


# Export Configuration Models
class ExportAgentResponse(BaseModel):
    """Export agent configuration response"""
    agent_config: Dict[str, Any]
    exported_at: str


class ImportAgentRequest(BaseModel):
    """Import agent configuration request"""
    agent_config: Dict[str, Any]


# Dynamic Tool Management Models
class AttachToolsRequest(BaseModel):
    """Request to attach tools to an agent"""
    tool_names: List[str] = Field(..., description="List of tool names to attach")


class DetachToolsRequest(BaseModel):
    """Request to detach tools from an agent"""
    tool_names: List[str] = Field(..., description="List of tool names to detach")


class AgentToolsResponse(BaseResponse):
    """Response with agent's current tools"""
    agent_id: str
    tools: List[str] = []
