"""
Dynamic Agent Management System for Google ADK
Handles agent creation, configuration, and lifecycle management
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from loguru import logger

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from pydantic import BaseModel, Field


@dataclass
class AgentPersona:
    """Agent persona configuration"""
    name: str
    description: str
    personality: str
    expertise: List[str] = field(default_factory=list)
    communication_style: str = "professional"
    language: str = "en"
    custom_instructions: str = ""
    examples: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Agent configuration parameters"""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_output_tokens: int = 2048
    top_p: float = 0.9
    top_k: int = 40
    safety_settings: Optional[List[Any]] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    name: str
    description: str
    persona: AgentPersona
    config: AgentConfig
    tools: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentManager:
    """
    Dynamic agent management system
    Handles agent creation, configuration, and lifecycle
    """
    
    def __init__(self, tool_manager, memory_manager, database_service=None):
        """
        Initialize agent manager
        
        Args:
            tool_manager: Tool manager instance
            memory_manager: Memory manager instance
            database_service: Database service instance for persistence
        """
        self.tool_manager = tool_manager
        self.memory_manager = memory_manager
        self.db_service = database_service
        
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_instances: Dict[str, LlmAgent] = {}
        self._lock = Lock()
        
        # Debug tracking
        self._agent_creation_count = 0
        self._agent_usage_stats = {}
        
        # Load agents from database if available
        if self.db_service:
            self._load_agents_from_db()
        
        logger.info("Agent manager initialized")
        logger.debug(f"DEBUG: AgentManager.__init__ - Tool manager: {type(tool_manager)}, Memory manager: {type(memory_manager)}, DB: {database_service is not None}")

    def create_agent(self,
                    name: str,
                    persona: AgentPersona,
                    config: Optional[AgentConfig] = None,
                    tools: Optional[List[str]] = None,
                    agent_id: Optional[str] = None,
                    planner: Optional[str] = None,
                    agent_type: Optional[str] = None,
                    sub_agents: Optional[List[str]] = None,
                    output_key: Optional[str] = None) -> str:
        """
        Create a new dynamic agent
        
        Args:
            name: Agent name
            persona: Agent persona configuration
            config: Agent configuration parameters
            tools: List of tool names to attach
            agent_id: Optional custom agent ID
            planner: Optional planner type
            agent_type: Optional agent type (SequentialAgent, ParallelAgent)
            sub_agents: Optional list of sub-agent IDs for team agents
            
        Returns:
            str: Agent ID
        """
        try:
            self._agent_creation_count += 1
            creation_id = f"creation_{self._agent_creation_count}"
            
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Starting agent creation")
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Input params: name='{name}', agent_type='{agent_type}', tools={tools}, sub_agents={sub_agents}")
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Persona: {persona.name} - {persona.description}")
            
            # Generate agent ID
            if not agent_id:
                agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Generated agent_id: {agent_id}")
            
            # Use default config if not provided
            if not config:
                config = AgentConfig()
            
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Config: model={config.model}, temp={config.temperature}, max_tokens={config.max_output_tokens}")
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                name=name,
                description=persona.description,
                persona=persona,
                config=config,
                tools=tools or []
            )
            
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - AgentInfo created: {agent_info.agent_id}")
            
            # Build instruction from persona
            instruction = self._build_instruction(persona)
            # logger.debug(f"DEBUG: create_agent ({creation_id}) - Built instruction length: {len(instruction)}")
            
            # Get tools from registry (including agent tools)
            agent_tools = []
            if tools:
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Requesting tools: {tools}")
                agent_tools = self.tool_manager.get_tools_for_agent(tools, agent_manager=self)
                # logger.debug(f"DEBUG: create_agent ({creation_id}) - Retrieved {len(agent_tools)} tools: {[getattr(t, 'name', str(t)) for t in agent_tools]}")
            
            # Create generate content config
            generate_config = types.GenerateContentConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                top_k=config.top_k,
                safety_settings=config.safety_settings or []
            )
            logger.debug(f"DEBUG: create_agent ({creation_id}) - GenerateContentConfig created: {generate_config}")
            
            # Create LLM model
            if config.model.startswith(("openai/", "anthropic/", "ollama/")):
                model = LiteLlm(model=config.model)
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Created LiteLlm model: {config.model}")
            else:
                model = config.model
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Using direct model: {config.model}")
            
            # Create ADK agent based on type
            logger.debug(f"DEBUG: create_agent ({creation_id}) - Creating agent type: {agent_type or 'regular'}")
            
            if agent_type == "SequentialAgent":
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Creating SequentialAgent with sub_agents: {sub_agents}")
                
                # Create Sequential Coordinator using AgentTool delegation (more reliable)
                if not sub_agents:
                    raise ValueError("Sequential agent requires sub_agents")
                
                # Create agent tools for each sub-agent
                sequential_tools = []
                for sub_agent_id in sub_agents:
                    logger.debug(f"DEBUG: create_agent ({creation_id}) - Checking sub-agent: {sub_agent_id}")
                    if not self.get_agent_info(sub_agent_id):
                        raise ValueError(f"Sub-agent {sub_agent_id} not found")
                    sequential_tools.append(f"agent:{sub_agent_id}")
                
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Sequential tools: {sequential_tools}")
                
                # Get tools from registry (including agent delegation tools)
                agent_tools = self.tool_manager.get_tools_for_agent(sequential_tools, agent_manager=self)
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Sequential agent tools count: {len(agent_tools)}")
                
                # Create enhanced instruction for sequential coordination
                sequential_instruction = f"""You are a Sequential Coordinator Agent. Your role is to coordinate tasks across multiple specialized sub-agents in a sequential manner.

Sub-agents available:
{chr(10).join([f"- {sub_id}: Use agent:{sub_id} tool to delegate tasks" for sub_id in sub_agents])}

SEQUENTIAL WORKFLOW RULES:
1. For simple queries, delegate to the most appropriate single sub-agent
2. For complex tasks, break them down and delegate sequentially
3. Always use the agent:sub_agent_id tools for delegation
4. Coordinate results from multiple sub-agents when needed
5. Provide a unified, coherent response

Original persona: {persona.description}"""
                
                # Create regular LLM agent with agent delegation tools
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=persona.description,
                    instruction=sequential_instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    output_key=output_key or f"{agent_id}_response"
                )
                
                # Store sub-agent information in metadata
                agent_info.metadata["agent_type"] = "SequentialCoordinator"
                agent_info.metadata["sub_agents"] = sub_agents
                agent_info.metadata["workflow_pattern"] = "sequential"
                agent_info.metadata["coordination_method"] = "agent_tools"
                logger.info(f"Created Sequential Coordinator with {len(sub_agents)} sub-agents: {sub_agents}")
                
            elif agent_type == "ParallelAgent":
                # Create Parallel Coordinator using AgentTool delegation (more reliable)
                if not sub_agents:
                    raise ValueError("Parallel agent requires sub_agents")
                
                # Create agent tools for each sub-agent
                parallel_tools = []
                for sub_agent_id in sub_agents:
                    if not self.get_agent_info(sub_agent_id):
                        raise ValueError(f"Sub-agent {sub_agent_id} not found")
                    parallel_tools.append(f"agent:{sub_agent_id}")
                
                # Get tools from registry (including agent delegation tools)
                agent_tools = self.tool_manager.get_tools_for_agent(parallel_tools, agent_manager=self)
                
                # Create enhanced instruction for parallel coordination
                parallel_instruction = f"""You are a Parallel Coordinator Agent. Your role is to coordinate tasks across multiple specialized sub-agents in parallel when beneficial.

Sub-agents available:
{chr(10).join([f"- {sub_id}: Use agent:{sub_id} tool to delegate tasks" for sub_id in sub_agents])}

PARALLEL WORKFLOW RULES:
1. For tasks that can be split, delegate parts to different sub-agents simultaneously
2. For simple queries, delegate to the most appropriate single sub-agent
3. Always use the agent:sub_agent_id tools for delegation
4. Combine and synthesize results from multiple sub-agents
5. Provide a unified, coherent response

Original persona: {persona.description}"""
                
                # Create regular LLM agent with agent delegation tools
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=persona.description,
                    instruction=parallel_instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    output_key=output_key or f"{agent_id}_response"
                )
                
                # Store sub-agent information in metadata
                agent_info.metadata["agent_type"] = "ParallelCoordinator"
                agent_info.metadata["sub_agents"] = sub_agents
                agent_info.metadata["workflow_pattern"] = "parallel"
                agent_info.metadata["coordination_method"] = "agent_tools"
                logger.info(f"Created Parallel Coordinator with {len(sub_agents)} sub-agents: {sub_agents}")
                
            else:
                # Create regular LLM agent with optional planner
                planner_instance = None
                
                if planner == "PlanReActPlanner":
                    from google.adk.planners import PlanReActPlanner
                    planner_instance = PlanReActPlanner()
                    logger.info(f"Adding PlanReActPlanner to agent {agent_id} - enables structured PLANNING->ACTION->REASONING->FINAL_ANSWER format")
                    
                elif planner == "BuiltInPlanner":
                    from google.adk.planners import BuiltInPlanner
                    # Configure thinking budget based on agent complexity
                    thinking_budget = 512  # Default
                    if len(agent_tools) > 3:  # More complex agents get more thinking tokens
                        thinking_budget = 1024
                    
                    planner_instance = BuiltInPlanner(
                        thinking_config=types.ThinkingConfig(
                            include_thoughts=True,
                            thinking_budget=thinking_budget
                        )
                    )
                    logger.info(f"Adding BuiltInPlanner to agent {agent_id} with thinking_budget={thinking_budget}")
                    
                elif planner == "BuiltInPlannerAdvanced":
                    from google.adk.planners import BuiltInPlanner
                    # Advanced configuration for complex reasoning tasks
                    planner_instance = BuiltInPlanner(
                        thinking_config=types.ThinkingConfig(
                            include_thoughts=True,
                            thinking_budget=2048  # More thinking tokens for complex tasks
                        )
                    )
                    logger.info(f"Adding Advanced BuiltInPlanner to agent {agent_id} with extended thinking capacity")
                
                # Enhance instruction for planner-enabled agents
                if planner_instance:
                    if planner == "PlanReActPlanner":
                        enhanced_instruction = f"""{instruction}

IMPORTANT: You MUST follow the ReAct methodology structure in your responses:

/*PLANNING*/
Create a detailed step-by-step plan for the task

/*ACTION*/
Execute the planned actions using available tools

/*REASONING*/
Explain your reasoning and observations from the actions

/*FINAL_ANSWER*/
Provide a comprehensive final answer based on your analysis

Always think systematically and use tools strategically."""
                    else:
                        enhanced_instruction = f"""{instruction}

You have advanced thinking capabilities. Use your internal reasoning to plan and structure your approach before responding. Think through problems step by step."""
                else:
                    enhanced_instruction = instruction
                
                # Create agent with planner
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Creating LlmAgent with planner: {planner}")
                logger.debug(f"DEBUG: create_agent ({creation_id}) - Enhanced instruction length: {len(enhanced_instruction)}")
                
                if planner_instance:
                    adk_agent = LlmAgent(
                        model=model,
                        name=agent_id,
                        description=persona.description,
                        instruction=enhanced_instruction,
                        tools=agent_tools,
                        generate_content_config=generate_config,
                        planner=planner_instance,
                        output_key=output_key or f"{agent_id}_response"
                    )
                else:
                    adk_agent = LlmAgent(
                        model=model,
                        name=agent_id,
                        description=persona.description,
                        instruction=enhanced_instruction,
                        tools=agent_tools,
                        generate_content_config=generate_config,
                        output_key=output_key or f"{agent_id}_response"
                    )
                
                logger.debug(f"DEBUG: create_agent ({creation_id}) - LlmAgent created successfully: {type(adk_agent)}")
            
            # Store agent
            logger.debug(f"DEBUG: create_agent ({creation_id}) - Storing agent in registry")
            
            with self._lock:
                self._agents[agent_id] = agent_info
                self._agent_instances[agent_id] = adk_agent
                
                # Update usage stats
                self._agent_usage_stats[agent_id] = {
                    "created_at": datetime.now(),
                    "creation_id": creation_id,
                    "agent_type": agent_type or "regular",
                    "tools_count": len(agent_tools),
                    "has_planner": planner is not None
                }
            
            # Save to database
            if self.db_service:
                try:
                    # Store agent type and planner in metadata
                    agent_info.metadata["agent_type"] = agent_type or "regular"
                    agent_info.metadata["planner"] = planner
                    agent_info.metadata["output_key"] = output_key
                    if sub_agents:
                        agent_info.metadata["sub_agents"] = sub_agents
                    
                    self._save_agent_to_db(agent_info)
                    logger.info(f"Agent {agent_id} saved to database")
                except Exception as e:
                    logger.error(f"Failed to save agent {agent_id} to database: {e}")
            
            logger.debug(f"DEBUG: create_agent ({creation_id}) - Agent stored successfully")
            logger.debug(f"DEBUG: create_agent ({creation_id}) - Total agents in registry: {len(self._agents)}")
            
            logger.info(f"Created agent '{name}' with ID {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create agent '{name}': {e}")
            raise

    def _initialize_agent(self, agent_id: str, name: str, persona: AgentPersona, 
                          config: AgentConfig, tools: List[str], planner: Optional[str] = None,
                          agent_type: Optional[str] = None, sub_agents: Optional[List[str]] = None) -> Optional[LlmAgent]:
        """Initialize an agent instance from stored configuration"""
        try:
            logger.info(f"Initializing agent {agent_id}")
            
            # Build instruction from persona
            instruction = self._build_instruction(persona)
            
            # Get tools from registry
            agent_tools = []
            if tools:
                agent_tools = self.tool_manager.get_tools_for_agent(tools, agent_manager=self)
            
            # Create generate content config
            generate_config = types.GenerateContentConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                top_k=config.top_k,
                safety_settings=config.safety_settings or []
            )
            
            # Create LLM model
            if config.model.startswith(("openai/", "anthropic/", "ollama/")):
                model = LiteLlm(model=config.model)
            else:
                model = config.model
            
            # Create planner if specified
            planner_instance = None
            if planner == "PlanReActPlanner":
                from google.adk.planners import PlanReActPlanner
                planner_instance = PlanReActPlanner()
                logger.info(f"Adding PlanReActPlanner to agent {agent_id}")
            elif planner == "BuiltInPlanner":
                from google.adk.planners import BuiltInPlanner
                thinking_budget = 1024 if len(agent_tools) > 3 else 512
                planner_instance = BuiltInPlanner(
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True,
                        thinking_budget=thinking_budget
                    )
                )
                logger.info(f"Adding BuiltInPlanner to agent {agent_id}")
            
            # Enhance instruction for planner
            if planner_instance:
                if planner == "PlanReActPlanner":
                    enhanced_instruction = f"""{instruction}

IMPORTANT: You MUST follow the ReAct methodology structure in your responses:

/*PLANNING*/
Create a detailed step-by-step plan for the task

/*ACTION*/
Execute the planned actions using available tools

/*REASONING*/
Explain your reasoning and observations from the actions

/*FINAL_ANSWER*/
Provide a comprehensive final answer based on your analysis

Always think systematically and use tools strategically."""
                else:
                    enhanced_instruction = f"""{instruction}

You have advanced thinking capabilities. Use your internal reasoning to plan and structure your approach before responding."""
            else:
                enhanced_instruction = instruction
            
            # Create agent
            if planner_instance:
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=persona.description,
                    instruction=enhanced_instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    planner=planner_instance,
                    output_key=f"{agent_id}_response"
                )
            else:
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=persona.description,
                    instruction=enhanced_instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    output_key=f"{agent_id}_response"
                )
            
            logger.info(f"Successfully initialized agent {agent_id}")
            return adk_agent
            
        except Exception as e:
            logger.error(f"Failed to initialize agent {agent_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_agent(self, agent_id: str) -> Optional[LlmAgent]:
        """Get agent instance by ID - auto-initializes if needed"""
        with self._lock:
            logger.debug(f"DEBUG: get_agent - Looking for agent {agent_id}")
            logger.debug(f"DEBUG: get_agent - Available instances: {list(self._agent_instances.keys())}")
            logger.debug(f"DEBUG: get_agent - Available agent infos: {list(self._agents.keys())}")
            
            # Check if it's a team agent (ADK agent stored directly)
            if agent_id in self._agent_instances:
                agent_instance = self._agent_instances.get(agent_id)
                logger.debug(f"DEBUG: get_agent - Found agent instance {agent_id}: {type(agent_instance)}")
                
                # Update usage stats if agent info exists
                agent_info = self._agents.get(agent_id)
                if agent_info and agent_info.is_active:
                    agent_info.usage_count += 1
                    agent_info.last_used = datetime.now()
                    logger.debug(f"DEBUG: get_agent - Updated usage stats for {agent_id}: count={agent_info.usage_count}")
                
                return agent_instance
            
            # Agent not in instances but exists in agent_infos - try to initialize it
            if agent_id in self._agents:
                logger.info(f"Agent {agent_id} exists but not initialized - initializing now")
                agent_info = self._agents[agent_id]
                
                try:
                    # Initialize the agent
                    agent_instance = self._initialize_agent(
                        agent_id=agent_id,
                        name=agent_info.name,
                        persona=agent_info.persona,
                        config=agent_info.config,
                        tools=agent_info.tools,
                        planner=agent_info.metadata.get("planner"),
                        agent_type=agent_info.metadata.get("agent_type"),
                        sub_agents=agent_info.metadata.get("sub_agents", [])
                    )
                    
                    if agent_instance:
                        self._agent_instances[agent_id] = agent_instance
                        logger.info(f"Successfully initialized agent {agent_id}")
                        
                        # Update usage stats
                        agent_info.usage_count += 1
                        agent_info.last_used = datetime.now()
                        
                        return agent_instance
                    else:
                        logger.error(f"Failed to initialize agent {agent_id}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Error initializing agent {agent_id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return None
            
            logger.debug(f"DEBUG: get_agent - Agent {agent_id} not found")
            return None

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information by ID"""
        with self._lock:
            return self._agents.get(agent_id)
    
    def is_team_agent(self, agent_id: str) -> bool:
        """Check if agent is a team agent"""
        agent_info = self.get_agent_info(agent_id)
        if not agent_info:
            return False
        return agent_info.metadata.get("agent_type") in ["SequentialAgent", "ParallelAgent"]
    
    def get_sub_agents(self, agent_id: str) -> List[str]:
        """Get sub-agent IDs for a team agent"""
        agent_info = self.get_agent_info(agent_id)
        if not agent_info:
            return []
        return agent_info.metadata.get("sub_agents", [])

    def update_agent_config(self, agent_id: str, config: AgentConfig) -> bool:
        """Update agent configuration"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                # Update config
                agent_info.config = config
                
                # Recreate agent with new config
                self._recreate_agent(agent_id)
            
            logger.info(f"Updated configuration for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} config: {e}")
            return False

    def update_agent_persona(self, agent_id: str, persona: AgentPersona) -> bool:
        """Update agent persona"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                # Update persona
                agent_info.persona = persona
                agent_info.description = persona.description
                
                # Recreate agent with new persona
                self._recreate_agent(agent_id)
            
            logger.info(f"Updated persona for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} persona: {e}")
            return False

    def update_agent_tools(self, agent_id: str, tools: List[str]) -> bool:
        """Update agent tools and save to database"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                # Update tools
                agent_info.tools = tools
                
                # Save to database
                if self.db_service:
                    self.db_service.update_agent(agent_id, {"tools": tools})
                
                # Recreate agent with new tools
                self._recreate_agent(agent_id)
            
            logger.info(f"Updated tools for agent {agent_id}: {tools}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} tools: {e}")
            return False

    def add_tool_to_agent(self, agent_id: str, tool_name: str) -> bool:
        """Add a tool to an agent"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                if tool_name not in agent_info.tools:
                    agent_info.tools.append(tool_name)
                    self._recreate_agent(agent_id)
                    
            logger.info(f"Added tool '{tool_name}' to agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add tool to agent {agent_id}: {e}")
            return False

    def remove_tool_from_agent(self, agent_id: str, tool_name: str) -> bool:
        """Remove a tool from an agent"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                if tool_name in agent_info.tools:
                    agent_info.tools.remove(tool_name)
                    self._recreate_agent(agent_id)
                    
            logger.info(f"Removed tool '{tool_name}' from agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove tool from agent {agent_id}: {e}")
            return False

    def list_agents(self, active_only: bool = True) -> List[AgentInfo]:
        """List all agents"""
        with self._lock:
            agents = []
            for agent_info in self._agents.values():
                if active_only and not agent_info.is_active:
                    continue
                agents.append(agent_info)
            
            return sorted(agents, key=lambda x: x.created_at, reverse=True)

    def search_agents(self, query: str) -> List[AgentInfo]:
        """Search agents by name or description"""
        query_lower = query.lower()
        matches = []
        
        with self._lock:
            for agent_info in self._agents.values():
                if not agent_info.is_active:
                    continue
                
                if (query_lower in agent_info.name.lower() or 
                    query_lower in agent_info.description.lower() or
                    any(query_lower in exp.lower() for exp in agent_info.persona.expertise)):
                    matches.append(agent_info)
        
        return sorted(matches, key=lambda x: x.usage_count, reverse=True)

    def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent"""
        with self._lock:
            agent_info = self._agents.get(agent_id)
            if agent_info:
                agent_info.is_active = True
                logger.info(f"Activated agent {agent_id}")
                return True
        return False

    def deactivate_agent(self, agent_id: str) -> bool:
        """Deactivate an agent"""
        with self._lock:
            agent_info = self._agents.get(agent_id)
            if agent_info:
                agent_info.is_active = False
                logger.info(f"Deactivated agent {agent_id}")
                return True
        return False

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent permanently"""
        try:
            with self._lock:
                if agent_id in self._agents:
                    del self._agents[agent_id]
                if agent_id in self._agent_instances:
                    del self._agent_instances[agent_id]
            
            logger.info(f"Deleted agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        with self._lock:
            total_agents = len(self._agents)
            active_agents = sum(1 for a in self._agents.values() if a.is_active)
            
            # Usage statistics
            usage_stats = {}
            for agent_info in self._agents.values():
                usage_stats[agent_info.agent_id] = agent_info.usage_count
            
            # Model distribution
            model_stats = {}
            for agent_info in self._agents.values():
                model = agent_info.config.model
                model_stats[model] = model_stats.get(model, 0) + 1
            
            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "inactive_agents": total_agents - active_agents,
                "most_used_agents": sorted(
                    usage_stats.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10],
                "model_distribution": model_stats,
                "total_usage": sum(usage_stats.values())
            }

    def export_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Export agent configuration"""
        with self._lock:
            agent_info = self._agents.get(agent_id)
            if not agent_info:
                return None
            
            return {
                "agent_id": agent_info.agent_id,
                "name": agent_info.name,
                "description": agent_info.description,
                "persona": {
                    "name": agent_info.persona.name,
                    "description": agent_info.persona.description,
                    "personality": agent_info.persona.personality,
                    "expertise": agent_info.persona.expertise,
                    "communication_style": agent_info.persona.communication_style,
                    "language": agent_info.persona.language,
                    "custom_instructions": agent_info.persona.custom_instructions,
                    "examples": agent_info.persona.examples
                },
                "config": {
                    "model": agent_info.config.model,
                    "temperature": agent_info.config.temperature,
                    "max_output_tokens": agent_info.config.max_output_tokens,
                    "top_p": agent_info.config.top_p,
                    "top_k": agent_info.config.top_k,
                    "timeout_seconds": agent_info.config.timeout_seconds,
                    "retry_attempts": agent_info.config.retry_attempts
                },
                "tools": agent_info.tools,
                "version": agent_info.version,
                "metadata": agent_info.metadata,
                "exported_at": datetime.now().isoformat()
            }

    def import_agent_config(self, config_data: Dict[str, Any]) -> Optional[str]:
        """Import agent from configuration"""
        try:
            # Create persona
            persona_data = config_data["persona"]
            persona = AgentPersona(
                name=persona_data["name"],
                description=persona_data["description"],
                personality=persona_data["personality"],
                expertise=persona_data.get("expertise", []),
                communication_style=persona_data.get("communication_style", "professional"),
                language=persona_data.get("language", "en"),
                custom_instructions=persona_data.get("custom_instructions", ""),
                examples=persona_data.get("examples", [])
            )
            
            # Create config
            config_info = config_data["config"]
            config = AgentConfig(
                model=config_info["model"],
                temperature=config_info.get("temperature", 0.7),
                max_output_tokens=config_info.get("max_output_tokens", 2048),
                top_p=config_info.get("top_p", 0.9),
                top_k=config_info.get("top_k", 40),
                timeout_seconds=config_info.get("timeout_seconds", 30),
                retry_attempts=config_info.get("retry_attempts", 3)
            )
            
            # Create agent
            agent_id = self.create_agent(
                name=config_data["name"],
                persona=persona,
                config=config,
                tools=config_data.get("tools", []),
                agent_id=config_data.get("agent_id")
            )
            
            logger.info(f"Imported agent configuration: {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to import agent configuration: {e}")
            return None

    def _build_instruction(self, persona: AgentPersona) -> str:
        """Build agent instruction from persona"""
        instruction_parts = []
        
        # Basic persona
        instruction_parts.append(f"You are {persona.name}.")
        # instruction_parts.append(persona.description)
        
        # Personality
        if persona.personality:
            instruction_parts.append(f"Your personality: {persona.personality}")
        
        # Expertise
        # if persona.expertise:
        #     expertise_str = ", ".join(persona.expertise)
        #     instruction_parts.append(f"Your areas of expertise: {expertise_str}")
        
        # Communication style
        if persona.communication_style:
            instruction_parts.append(f"Communication style: {persona.communication_style}")
        
        # Language
        if persona.language and persona.language != "en":
            instruction_parts.append(f"Respond primarily in {persona.language}")
        
        # Custom instructions
        if persona.custom_instructions:
            instruction_parts.append(persona.custom_instructions)
        
        # Examples
        # if persona.examples:
        #     instruction_parts.append("\nExamples:")
        #     for i, example in enumerate(persona.examples, 1):
        #         instruction_parts.append(f"Example {i}:")
        #         instruction_parts.append(f"User: {example.get('user', '')}")
        #         instruction_parts.append(f"Assistant: {example.get('assistant', '')}")
        
        return "\n\n".join(instruction_parts)

    def _recreate_agent(self, agent_id: str):
        """Recreate agent instance with updated configuration"""
        try:
            agent_info = self._agents[agent_id]
            
            # Build instruction
            instruction = self._build_instruction(agent_info.persona)
            
            # Get tools (including agent tools and shared memory tools)
            agent_tools = []
            if agent_info.tools:
                agent_tools = self.tool_manager.get_tools_for_agent(
                    tool_names=agent_info.tools,
                    agent_manager=self,
                    memory_manager=self.memory_manager,
                    user_id="system",  # Default user for agent creation
                    agent_id=agent_id
                )
            
            # Create generate content config
            generate_config = types.GenerateContentConfig(
                temperature=agent_info.config.temperature,
                max_output_tokens=agent_info.config.max_output_tokens,
                top_p=agent_info.config.top_p,
                top_k=agent_info.config.top_k,
                safety_settings=agent_info.config.safety_settings or []
            )
            
            # Create model
            if agent_info.config.model.startswith(("openai/", "anthropic/", "ollama/")):
                model = LiteLlm(model=agent_info.config.model)
            else:
                model = agent_info.config.model
            
            # Get planner configuration from metadata
            planner = agent_info.metadata.get('planner')
            planner_instance = None
            
            # Create planner if specified
            if planner == "PlanReActPlanner":
                from google.adk.planners import PlanReActPlanner
                planner_instance = PlanReActPlanner()
                logger.info(f"Adding PlanReActPlanner to agent {agent_id} during recreation")
                
                # Enhance instruction for ReAct methodology
                instruction = f"""{instruction}

IMPORTANT: You MUST follow the ReAct methodology structure in your responses:
1. **PLANNING**: Analyze the task and create a step-by-step plan
2. **ACTION**: Execute each step using available tools
3. **REASONING**: Reflect on the results and adjust the plan if needed
4. **FINAL ANSWER**: Provide a comprehensive response based on your findings

Use this structured approach for complex queries that require multiple steps or tool usage."""
                
            elif planner == "BuiltInPlanner":
                from google.adk.planners import BuiltInPlanner
                thinking_budget = 1024 if len(agent_tools) > 3 else 512
                planner_instance = BuiltInPlanner(thinking_budget=thinking_budget)
                logger.info(f"Adding BuiltInPlanner to agent {agent_id} during recreation (thinking_budget: {thinking_budget})")
            
            # Create new agent instance with planner
            if planner_instance:
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=agent_info.persona.description,
                    instruction=instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    planner=planner_instance,
                    output_key=f"{agent_id}_response"
                )
            else:
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=agent_info.persona.description,
                    instruction=instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    output_key=f"{agent_id}_response"
                )
            
            # Replace instance
            self._agent_instances[agent_id] = adk_agent
            logger.info(f"Successfully recreated agent {agent_id} with planner: {planner}")
            return True
            
        except Exception as e:
            logger.error(f"Error recreating agent {agent_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def create_team_agent(self, team_id: str, team_name: str, team_description: str, 
                         team_type: str, agent_ids: List[str]) -> str:
        """
        Create a team agent from team manager data
        
        Args:
            team_id: Team identifier
            team_name: Team name
            team_description: Team description
            team_type: Team type (sequential, parallel, hierarchical)
            agent_ids: List of sub-agent IDs
            
        Returns:
            str: Created agent ID
        """
        try:
            # Create persona for team agent
            persona = AgentPersona(
                name=f"{team_name} Coordinator",
                description=team_description,
                personality="collaborative and coordinating",
                expertise=["team coordination", "task delegation"],
                communication_style="professional"
            )
            
            # Map team types to agent types
            agent_type_map = {
                "sequential": "SequentialAgent",
                "parallel": "ParallelAgent",
                "hierarchical": "LlmAgent"  # Hierarchical uses regular agent with agent tools
            }
            
            agent_type = agent_type_map.get(team_type, "LlmAgent")
            
            # For hierarchical teams, create agent tools for delegation
            tools = []
            if team_type == "hierarchical":
                tools = [f"agent:{agent_id}" for agent_id in agent_ids]
            
            # Create the agent
            created_agent_id = self.create_agent(
                name=team_name,
                persona=persona,
                agent_id=team_id,  # Use team_id as agent_id
                agent_type=agent_type,
                sub_agents=agent_ids if agent_type != "LlmAgent" else None,
                tools=tools
            )
            
            # Add team metadata
            with self._lock:
                agent_info = self._agents.get(created_agent_id)
                if agent_info:
                    agent_info.metadata.update({
                        "is_team_agent": True,
                        "team_type": team_type,
                        "original_team_id": team_id,
                        "member_agents": agent_ids
                    })
            
            logger.info(f"Created team agent {created_agent_id} for team {team_id} ({team_type})")
            return created_agent_id
            
        except Exception as e:
            logger.error(f"Failed to create team agent for {team_id}: {e}")
            raise
    
    # ==================== DATABASE PERSISTENCE METHODS ====================
    
    def _load_agents_from_db(self):
        """Load all agents from database into memory"""
        try:
            if not self.db_service:
                return
            
            db_agents = self.db_service.get_all_agents(include_inactive=False)
            logger.info(f"Loading {len(db_agents)} agents from database")
            
            for db_agent in db_agents:
                try:
                    # Reconstruct AgentPersona
                    persona = AgentPersona(
                        name=db_agent.persona_name or db_agent.name,
                        description=db_agent.persona_description or db_agent.description,
                        personality=db_agent.persona_personality or "professional",
                        expertise=db_agent.persona_expertise or [],
                        communication_style=db_agent.persona_communication_style or "professional",
                        language=db_agent.persona_language or "en",
                        custom_instructions=db_agent.persona_custom_instructions or "",
                        examples=db_agent.persona_examples or []
                    )
                    
                    # Reconstruct AgentConfig
                    config_data = db_agent.config or {}
                    config = AgentConfig(
                        model=config_data.get("model", "gemini-2.0-flash"),
                        temperature=config_data.get("temperature", 0.7),
                        max_output_tokens=config_data.get("max_output_tokens", 2048),
                        top_p=config_data.get("top_p", 0.9),
                        top_k=config_data.get("top_k", 40),
                        safety_settings=config_data.get("safety_settings"),
                        timeout_seconds=config_data.get("timeout_seconds", 30),
                        retry_attempts=config_data.get("retry_attempts", 3)
                    )
                    
                    # Create AgentInfo
                    agent_info = AgentInfo(
                        agent_id=db_agent.agent_id,
                        name=db_agent.name,
                        description=db_agent.description,
                        persona=persona,
                        config=config,
                        tools=db_agent.tools or [],
                        created_at=db_agent.created_at,
                        last_used=db_agent.last_used,
                        usage_count=db_agent.usage_count,
                        is_active=db_agent.is_active,
                        version=db_agent.version,
                        metadata=db_agent.agent_metadata or {}
                    )
                    
                    # Store in memory (but don't create ADK instance yet - lazy loading)
                    self._agents[db_agent.agent_id] = agent_info
                    logger.debug(f"Loaded agent from DB: {db_agent.agent_id}")
                    
                except Exception as e:
                    logger.error(f"Error loading agent {db_agent.agent_id} from DB: {e}")
                    continue
            
            logger.info(f"Successfully loaded {len(self._agents)} agents from database")
            
        except Exception as e:
            logger.error(f"Error loading agents from database: {e}")
    
    def _save_agent_to_db(self, agent_info: AgentInfo):
        """Save agent to database"""
        try:
            if not self.db_service:
                return
            
            # Prepare agent data for database
            agent_data = {
                "agent_id": agent_info.agent_id,
                "name": agent_info.name,
                "description": agent_info.description,
                "agent_type": agent_info.metadata.get("agent_type", "regular"),
                "persona_name": agent_info.persona.name,
                "persona_description": agent_info.persona.description,
                "persona_personality": agent_info.persona.personality,
                "persona_expertise": agent_info.persona.expertise,
                "persona_communication_style": agent_info.persona.communication_style,
                "persona_language": agent_info.persona.language,
                "persona_custom_instructions": agent_info.persona.custom_instructions,
                "persona_examples": agent_info.persona.examples,
                "config": {
                    "model": agent_info.config.model,
                    "temperature": agent_info.config.temperature,
                    "max_output_tokens": agent_info.config.max_output_tokens,
                    "top_p": agent_info.config.top_p,
                    "top_k": agent_info.config.top_k,
                    "timeout_seconds": agent_info.config.timeout_seconds,
                    "retry_attempts": agent_info.config.retry_attempts
                },
                "tools": agent_info.tools,
                "sub_agents": agent_info.metadata.get("sub_agents"),
                "planner": agent_info.metadata.get("planner"),
                "output_key": agent_info.metadata.get("output_key"),
                "version": agent_info.version,
                "is_active": agent_info.is_active,
                "usage_count": agent_info.usage_count,
                "created_at": agent_info.created_at,
                "last_used": agent_info.last_used,
                "agent_metadata": agent_info.metadata
            }
            
            self.db_service.save_agent(agent_data)
            logger.debug(f"Saved agent to DB: {agent_info.agent_id}")
            
        except Exception as e:
            logger.error(f"Error saving agent {agent_info.agent_id} to database: {e}")
    
    def ensure_agent_instance(self, agent_id: str) -> Optional[LlmAgent]:
        """
        Ensure agent instance exists, create if needed (lazy loading)
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Optional[LlmAgent]: Agent instance or None
        """
        # Check if instance already exists
        if agent_id in self._agent_instances:
            return self._agent_instances[agent_id]
        
        # Check if agent info exists
        agent_info = self._agents.get(agent_id)
        if not agent_info:
            # Try to load from database
            if self.db_service:
                db_agent = self.db_service.get_agent(agent_id)
                if db_agent:
                    # Reconstruct agent info
                    persona = AgentPersona(
                        name=db_agent.persona_name or db_agent.name,
                        description=db_agent.persona_description or db_agent.description,
                        personality=db_agent.persona_personality or "professional",
                        expertise=db_agent.persona_expertise or [],
                        communication_style=db_agent.persona_communication_style or "professional",
                        language=db_agent.persona_language or "en",
                        custom_instructions=db_agent.persona_custom_instructions or "",
                        examples=db_agent.persona_examples or []
                    )
                    
                    config_data = db_agent.config or {}
                    config = AgentConfig(
                        model=config_data.get("model", "gemini-2.0-flash"),
                        temperature=config_data.get("temperature", 0.7),
                        max_output_tokens=config_data.get("max_output_tokens", 2048),
                        top_p=config_data.get("top_p", 0.9),
                        top_k=config_data.get("top_k", 40),
                        timeout_seconds=config_data.get("timeout_seconds", 30),
                        retry_attempts=config_data.get("retry_attempts", 3)
                    )
                    
                    agent_info = AgentInfo(
                        agent_id=db_agent.agent_id,
                        name=db_agent.name,
                        description=db_agent.description,
                        persona=persona,
                        config=config,
                        tools=db_agent.tools or [],
                        created_at=db_agent.created_at,
                        last_used=db_agent.last_used,
                        usage_count=db_agent.usage_count,
                        is_active=db_agent.is_active,
                        version=db_agent.version,
                        metadata=db_agent.agent_metadata or {}
                    )
                    
                    self._agents[agent_id] = agent_info
                    logger.info(f"Loaded agent {agent_id} from database on-demand")
                else:
                    logger.warning(f"Agent {agent_id} not found in memory or database")
                    return None
            else:
                logger.warning(f"Agent {agent_id} not found and no database service available")
                return None
        
        # Create ADK agent instance
        try:
            instruction = self._build_instruction(agent_info.persona)
            agent_tools = []
            if agent_info.tools:
                agent_tools = self.tool_manager.get_tools_for_agent(agent_info.tools, agent_manager=self)
            
            generate_config = types.GenerateContentConfig(
                temperature=agent_info.config.temperature,
                max_output_tokens=agent_info.config.max_output_tokens,
                top_p=agent_info.config.top_p,
                top_k=agent_info.config.top_k,
                safety_settings=agent_info.config.safety_settings or []
            )
            
            if agent_info.config.model.startswith(("openai/", "anthropic/", "ollama/")):
                model = LiteLlm(model=agent_info.config.model)
            else:
                model = agent_info.config.model
            
            adk_agent = LlmAgent(
                model=model,
                name=agent_info.name,
                description=agent_info.description,
                instruction=instruction,
                tools=agent_tools,
                generate_content_config=generate_config
            )
            
            self._agent_instances[agent_id] = adk_agent
            logger.info(f"Created ADK instance for agent {agent_id}")
            
            # Update usage stats
            if self.db_service:
                self.db_service.update_agent_usage(agent_id)
            
            return adk_agent
            
        except Exception as e:
            logger.error(f"Error creating agent instance for {agent_id}: {e}")
            return None
