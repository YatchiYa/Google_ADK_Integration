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
    
    def __init__(self, tool_manager, memory_manager):
        """
        Initialize agent manager
        
        Args:
            tool_manager: Tool manager instance
            memory_manager: Memory manager instance
        """
        self.tool_manager = tool_manager
        self.memory_manager = memory_manager
        
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_instances: Dict[str, LlmAgent] = {}
        self._lock = Lock()
        
        logger.info("Agent manager initialized")

    def create_agent(self,
                    name: str,
                    persona: AgentPersona,
                    config: Optional[AgentConfig] = None,
                    tools: Optional[List[str]] = None,
                    agent_id: Optional[str] = None,
                    planner: Optional[str] = None,
                    agent_type: Optional[str] = None,
                    sub_agents: Optional[List[str]] = None) -> str:
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
            # Generate agent ID
            if not agent_id:
                agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            
            # Use default config if not provided
            if not config:
                config = AgentConfig()
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                name=name,
                description=persona.description,
                persona=persona,
                config=config,
                tools=tools or []
            )
            
            # Build instruction from persona
            instruction = self._build_instruction(persona)
            
            # Get tools from registry (including agent tools)
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
            
            # Create ADK agent based on type
            if agent_type == "SequentialAgent":
                # Create REAL Sequential Team Agent using ADK classes
                if not sub_agents:
                    raise ValueError("Sequential agent requires sub_agents")
                
                # Get actual sub-agent instances (not IDs)
                sub_agent_instances = []
                for sub_agent_id in sub_agents:
                    sub_agent = self.get_agent(sub_agent_id)
                    if not sub_agent:
                        raise ValueError(f"Sub-agent {sub_agent_id} not found")
                    sub_agent_instances.append(sub_agent)
                
                # Use REAL ADK SequentialAgent class
                from google.adk.agents import SequentialAgent
                adk_agent = SequentialAgent(
                    name=agent_id,
                    sub_agents=sub_agent_instances,
                    description=persona.description
                )
                
                # Store sub-agent information in metadata
                agent_info.metadata["agent_type"] = "SequentialAgent"
                agent_info.metadata["sub_agents"] = sub_agents
                logger.info(f"Created REAL SequentialAgent with {len(sub_agents)} sub-agents: {sub_agents}")
                
            elif agent_type == "ParallelAgent":
                # Create REAL Parallel Team Agent using ADK classes
                if not sub_agents:
                    raise ValueError("Parallel agent requires sub_agents")
                
                # Get actual sub-agent instances (not IDs)
                sub_agent_instances = []
                for sub_agent_id in sub_agents:
                    sub_agent = self.get_agent(sub_agent_id)
                    if not sub_agent:
                        raise ValueError(f"Sub-agent {sub_agent_id} not found")
                    sub_agent_instances.append(sub_agent)
                
                # Use REAL ADK ParallelAgent class
                from google.adk.agents import ParallelAgent
                adk_agent = ParallelAgent(
                    name=agent_id,
                    sub_agents=sub_agent_instances,
                    description=persona.description
                )
                
                # Store sub-agent information in metadata
                agent_info.metadata["agent_type"] = "ParallelAgent"
                agent_info.metadata["sub_agents"] = sub_agents
                logger.info(f"Created REAL ParallelAgent with {len(sub_agents)} sub-agents: {sub_agents}")
                
            else:
                # Create regular LLM agent
                adk_agent = LlmAgent(
                    model=model,
                    name=agent_id,
                    description=persona.description,
                    instruction=instruction,
                    tools=agent_tools,
                    generate_content_config=generate_config,
                    output_key=f"{agent_id}_response"
                )
                
                # Add planner if specified
                if planner == "PlanReActPlanner":
                    from google.adk.planners import PlanReActPlanner
                    adk_agent.planner = PlanReActPlanner()
                    logger.info(f"Added PlanReActPlanner to agent {agent_id}")
            
            # Store agent
            with self._lock:
                self._agents[agent_id] = agent_info
                self._agent_instances[agent_id] = adk_agent
            
            logger.info(f"Created agent '{name}' with ID {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create agent '{name}': {e}")
            raise

    def get_agent(self, agent_id: str) -> Optional[LlmAgent]:
        """Get agent instance by ID"""
        with self._lock:
            agent_info = self._agents.get(agent_id)
            if agent_info and agent_info.is_active:
                # Update usage stats
                agent_info.usage_count += 1
                agent_info.last_used = datetime.now()
                
                return self._agent_instances.get(agent_id)
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
        """Update agent tools"""
        try:
            with self._lock:
                agent_info = self._agents.get(agent_id)
                if not agent_info:
                    return False
                
                # Update tools
                agent_info.tools = tools
                
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
        instruction_parts.append(persona.description)
        
        # Personality
        if persona.personality:
            instruction_parts.append(f"Your personality: {persona.personality}")
        
        # Expertise
        if persona.expertise:
            expertise_str = ", ".join(persona.expertise)
            instruction_parts.append(f"Your areas of expertise: {expertise_str}")
        
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
        if persona.examples:
            instruction_parts.append("\nExamples:")
            for i, example in enumerate(persona.examples, 1):
                instruction_parts.append(f"Example {i}:")
                instruction_parts.append(f"User: {example.get('user', '')}")
                instruction_parts.append(f"Assistant: {example.get('assistant', '')}")
        
        return "\n\n".join(instruction_parts)

    def _recreate_agent(self, agent_id: str):
        """Recreate agent instance with updated configuration"""
        agent_info = self._agents[agent_id]
        
        # Build instruction
        instruction = self._build_instruction(agent_info.persona)
        
        # Get tools (including agent tools)
        agent_tools = []
        if agent_info.tools:
            agent_tools = self.tool_manager.get_tools_for_agent(agent_info.tools, agent_manager=self)
        
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
        
        # Create new agent instance
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
