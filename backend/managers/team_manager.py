"""
Google ADK Multi-Agent Team Manager
Implements Sequential, Parallel, and Hierarchical team patterns using Google ADK
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from loguru import logger
from enum import Enum

from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types
from typing import AsyncGenerator


class TeamType(str, Enum):
    """Team execution patterns"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    LOOP = "loop"


@dataclass
class TeamInfo:
    """Information about a registered team"""
    team_id: str
    name: str
    description: str
    team_type: TeamType
    agent_ids: List[str]
    coordinator_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class TeamManager:
    """
    Multi-Agent Team Management System
    Implements Google ADK patterns for team coordination
    """
    
    def __init__(self, agent_manager):
        """
        Initialize team manager
        
        Args:
            agent_manager: Agent manager instance
        """
        self.agent_manager = agent_manager
        self._teams: Dict[str, TeamInfo] = {}
        self._team_agents: Dict[str, str] = {}  # team_id -> coordinator_agent_id
        self._lock = Lock()
        
        logger.info("Team manager initialized")

    def create_team(self, 
                   name: str,
                   description: str,
                   team_type: TeamType,
                   agent_ids: List[str],
                   team_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new multi-agent team
        
        Args:
            name: Team name
            description: Team description  
            team_type: Team execution pattern
            agent_ids: List of agent IDs to include
            team_id: Optional custom team ID
            metadata: Optional team metadata
            
        Returns:
            str: Team ID
        """
        try:
            # Generate team ID
            if not team_id:
                team_id = f"team_{uuid.uuid4().hex[:8]}"
            
            # Validate agents exist
            for agent_id in agent_ids:
                if not self.agent_manager.get_agent_info(agent_id):
                    raise ValueError(f"Agent {agent_id} not found")
            
            if len(agent_ids) < 2:
                raise ValueError("Team must have at least 2 agents")
            
            # Create coordinator agent based on team type
            coordinator_id = self._create_coordinator_agent(
                team_id, name, description, team_type, agent_ids
            )
            
            # Create team info
            team_info = TeamInfo(
                team_id=team_id,
                name=name,
                description=description,
                team_type=team_type,
                agent_ids=agent_ids,
                coordinator_id=coordinator_id,
                metadata=metadata or {}
            )
            
            # Store team
            with self._lock:
                self._teams[team_id] = team_info
                self._team_agents[team_id] = coordinator_id
            
            logger.info(f"Created {team_type} team '{name}' with ID {team_id}")
            return team_id
            
        except Exception as e:
            logger.error(f"Failed to create team '{name}': {e}")
            raise

    def _create_coordinator_agent(self, 
                                 team_id: str,
                                 team_name: str, 
                                 team_description: str,
                                 team_type: TeamType,
                                 agent_ids: List[str]) -> str:
        """Create actual ADK agent for the team"""
        
        if team_type == TeamType.SEQUENTIAL:
            return self._create_sequential_agent(
                team_id, team_name, team_description, agent_ids
            )
        elif team_type == TeamType.PARALLEL:
            return self._create_parallel_agent(
                team_id, team_name, team_description, agent_ids
            )
        elif team_type == TeamType.LOOP:
            return self._create_loop_agent(
                team_id, team_name, team_description, agent_ids
            )
        elif team_type == TeamType.HIERARCHICAL:
            return self._create_hierarchical_agent(
                team_id, team_name, team_description, agent_ids
            )
        else:
            raise ValueError(f"Unsupported team type: {team_type}")

    def _create_sequential_agent(self, 
                                   team_id: str,
                                   team_name: str,
                                   team_description: str, 
                                   agent_ids: List[str]) -> str:
        """Create actual ADK SequentialAgent"""
        
        # Get sub-agents from agent manager
        sub_agents = []
        for agent_id in agent_ids:
            agent_instance = self.agent_manager.get_agent(agent_id)
            if agent_instance:
                sub_agents.append(agent_instance)
            else:
                raise ValueError(f"Agent {agent_id} not found or inactive")
        
        # Create ADK SequentialAgent
        sequential_agent = SequentialAgent(
            name=team_id,
            description=f"Sequential team: {team_description}",
            sub_agents=sub_agents
        )
        
        # Store the ADK agent in agent manager's instances
        with self.agent_manager._lock:
            self.agent_manager._agent_instances[team_id] = sequential_agent
            logger.debug(f"Stored team agent {team_id} in _agent_instances")
            logger.debug(f"Current instances: {list(self.agent_manager._agent_instances.keys())}")
        
        logger.info(f"Created ADK SequentialAgent {team_id} with {len(sub_agents)} sub-agents")
        return team_id

    def _create_parallel_agent(self, 
                                 team_id: str,
                                 team_name: str,
                                 team_description: str,
                                 agent_ids: List[str]) -> str:
        """Create actual ADK ParallelAgent"""
        
        # Get sub-agents from agent manager
        sub_agents = []
        for agent_id in agent_ids:
            agent_instance = self.agent_manager.get_agent(agent_id)
            if agent_instance:
                sub_agents.append(agent_instance)
            else:
                raise ValueError(f"Agent {agent_id} not found or inactive")
        
        # Create ADK ParallelAgent
        parallel_agent = ParallelAgent(
            name=team_id,
            description=f"Parallel team: {team_description}",
            sub_agents=sub_agents
        )
        
        # Store the ADK agent in agent manager's instances
        with self.agent_manager._lock:
            self.agent_manager._agent_instances[team_id] = parallel_agent
        
        logger.info(f"Created ADK ParallelAgent {team_id} with {len(sub_agents)} sub-agents")
        return team_id

    def _create_loop_agent(self,
                          team_id: str,
                          team_name: str,
                          team_description: str,
                          agent_ids: List[str]) -> str:
        """Create actual ADK LoopAgent"""
        
        # Get sub-agents from agent manager
        sub_agents = []
        for agent_id in agent_ids:
            agent_instance = self.agent_manager.get_agent(agent_id)
            if agent_instance:
                sub_agents.append(agent_instance)
            else:
                raise ValueError(f"Agent {agent_id} not found or inactive")
        
        # Create ADK LoopAgent with default max iterations
        loop_agent = LoopAgent(
            name=team_id,
            description=f"Loop team: {team_description}",
            sub_agents=sub_agents,
            max_iterations=10  # Default, can be configured
        )
        
        # Store the ADK agent in agent manager's instances
        with self.agent_manager._lock:
            self.agent_manager._agent_instances[team_id] = loop_agent
        
        logger.info(f"Created ADK LoopAgent {team_id} with {len(sub_agents)} sub-agents")
        return team_id

    def _create_hierarchical_agent(self, 
                                  team_id: str,
                                  team_name: str,
                                  team_description: str,
                                  agent_ids: List[str]) -> str:
        """Create hierarchical coordinator using LlmAgent with sub_agents"""
        
        from managers.agent_manager import AgentPersona, AgentConfig
        
        # Get sub-agents from agent manager
        sub_agents = []
        for agent_id in agent_ids:
            agent_instance = self.agent_manager.get_agent(agent_id)
            if agent_instance:
                sub_agents.append(agent_instance)
            else:
                raise ValueError(f"Agent {agent_id} not found or inactive")
        
        # Build agent context information
        agent_context = "\n".join([
            f"- {agent_id}: Available for delegation via transfer_to_agent()"
            for agent_id in agent_ids
        ])
        
        persona = AgentPersona(
            name=f"{team_name} Hierarchical Coordinator", 
            description=f"Hierarchical coordinator for {team_description}. Uses LLM transfer for delegation.",
            personality="strategic, analytical, and leadership-oriented",
            expertise=["hierarchical coordination", "task decomposition", "strategic delegation"],
            communication_style="authoritative and comprehensive",
            custom_instructions=f"""
You are a Hierarchical Coordinator with access to specialized sub-agents via transfer_to_agent().

AVAILABLE AGENTS:
{agent_context}

HIERARCHICAL PATTERNS:
- **Strategic Analysis**: Analyze task complexity first
- **Agent Selection**: Choose the most appropriate agent for each sub-task
- **LLM Transfer**: Use transfer_to_agent(agent_name='agent_id') to delegate
- **Result Integration**: Synthesize outputs from multiple agents

DELEGATION RULES:
- For complex tasks, break them down and delegate parts to appropriate agents
- Use transfer_to_agent() to hand off control to sub-agents
- Coordinate multiple agents for comprehensive solutions
- Always provide clear context when transferring
"""
        )
        
        # Create hierarchical LlmAgent with sub_agents for transfer capability
        # Get tools from agent manager
        tools = self.agent_manager.tool_manager.get_tools_for_agent([], agent_manager=self.agent_manager)
        
        # Create generate content config
        generate_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.9,
            top_k=40
        )
        
        # Create hierarchical LlmAgent with sub_agents
        hierarchical_agent = LlmAgent(
            model="gemini-2.0-flash",
            name=team_id,
            description=persona.description,
            instruction=self.agent_manager._build_instruction(persona),
            tools=tools,
            generate_content_config=generate_config,
            sub_agents=sub_agents  # This enables transfer_to_agent()
        )
        
        # Store the ADK agent in agent manager's instances
        with self.agent_manager._lock:
            self.agent_manager._agent_instances[team_id] = hierarchical_agent
        
        logger.info(f"Created ADK Hierarchical LlmAgent {team_id} with {len(sub_agents)} sub-agents")
        return team_id

    def get_team(self, team_id: str) -> Optional[TeamInfo]:
        """Get team information by ID"""
        with self._lock:
            team_info = self._teams.get(team_id)
            if team_info and team_info.is_active:
                # Update usage stats
                team_info.usage_count += 1
                team_info.last_used = datetime.now()
                return team_info
        return None

    def get_team_coordinator(self, team_id: str) -> Optional[str]:
        """Get coordinator agent ID for a team"""
        with self._lock:
            return self._team_agents.get(team_id)

    def list_teams(self, active_only: bool = True) -> List[TeamInfo]:
        """List all teams"""
        with self._lock:
            teams = []
            for team_info in self._teams.values():
                if active_only and not team_info.is_active:
                    continue
                teams.append(team_info)
            
            return sorted(teams, key=lambda x: x.created_at, reverse=True)

    def update_team(self, 
                   team_id: str,
                   name: Optional[str] = None,
                   description: Optional[str] = None,
                   agent_ids: Optional[List[str]] = None) -> bool:
        """Update team configuration"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                # Update basic info
                if name:
                    team_info.name = name
                if description:
                    team_info.description = description
                
                # Update agents if provided
                if agent_ids:
                    # Validate new agents
                    for agent_id in agent_ids:
                        if not self.agent_manager.get_agent_info(agent_id):
                            raise ValueError(f"Agent {agent_id} not found")
                    
                    team_info.agent_ids = agent_ids
                    
                    # Recreate coordinator with new agents
                    old_coordinator = team_info.coordinator_id
                    new_coordinator = self._create_coordinator_agent(
                        team_id, team_info.name, team_info.description,
                        team_info.team_type, agent_ids
                    )
                    
                    team_info.coordinator_id = new_coordinator
                    self._team_agents[team_id] = new_coordinator
                    
                    # Clean up old coordinator
                    if old_coordinator:
                        self.agent_manager.delete_agent(old_coordinator)
            
            logger.info(f"Updated team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update team {team_id}: {e}")
            return False

    def add_agent_to_team(self, team_id: str, agent_id: str) -> bool:
        """Add an agent to a team"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                if not self.agent_manager.get_agent_info(agent_id):
                    raise ValueError(f"Agent {agent_id} not found")
                
                if agent_id not in team_info.agent_ids:
                    team_info.agent_ids.append(agent_id)
                    
                    # Update coordinator with new agent
                    self._update_coordinator_agents(team_info)
            
            logger.info(f"Added agent {agent_id} to team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add agent to team: {e}")
            return False

    def remove_agent_from_team(self, team_id: str, agent_id: str) -> bool:
        """Remove an agent from a team"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                if agent_id in team_info.agent_ids:
                    team_info.agent_ids.remove(agent_id)
                    
                    # Ensure team still has minimum agents
                    if len(team_info.agent_ids) < 2:
                        raise ValueError("Team must have at least 2 agents")
                    
                    # Update coordinator with remaining agents
                    self._update_coordinator_agents(team_info)
            
            logger.info(f"Removed agent {agent_id} from team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove agent from team: {e}")
            return False

    def _update_coordinator_agents(self, team_info: TeamInfo):
        """Update coordinator agent with new agent list"""
        coordinator_id = team_info.coordinator_id
        if coordinator_id:
            # Create new agent tools list
            tools = [f"agent:{agent_id}" for agent_id in team_info.agent_ids]
            
            # Update coordinator tools
            self.agent_manager.update_agent_tools(coordinator_id, tools)

    def activate_team(self, team_id: str) -> bool:
        """Activate a team"""
        with self._lock:
            team_info = self._teams.get(team_id)
            if team_info:
                team_info.is_active = True
                logger.info(f"Activated team {team_id}")
                return True
        return False

    def deactivate_team(self, team_id: str) -> bool:
        """Deactivate a team"""
        with self._lock:
            team_info = self._teams.get(team_id)
            if team_info:
                team_info.is_active = False
                logger.info(f"Deactivated team {team_id}")
                return True
        return False

    def delete_team(self, team_id: str) -> bool:
        """Delete a team permanently"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                # Delete coordinator agent
                if team_info.coordinator_id:
                    self.agent_manager.delete_agent(team_info.coordinator_id)
                
                # Remove team
                del self._teams[team_id]
                if team_id in self._team_agents:
                    del self._team_agents[team_id]
            
            logger.info(f"Deleted team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete team {team_id}: {e}")
            return False

    def get_team_stats(self) -> Dict[str, Any]:
        """Get team statistics"""
        with self._lock:
            total_teams = len(self._teams)
            active_teams = sum(1 for t in self._teams.values() if t.is_active)
            
            # Type distribution
            type_stats = {}
            for team_info in self._teams.values():
                team_type = team_info.team_type.value
                type_stats[team_type] = type_stats.get(team_type, 0) + 1
            
            # Usage statistics
            usage_stats = {}
            for team_info in self._teams.values():
                usage_stats[team_info.team_id] = team_info.usage_count
            
            return {
                "total_teams": total_teams,
                "active_teams": active_teams,
                "inactive_teams": total_teams - active_teams,
                "type_distribution": type_stats,
                "most_used_teams": sorted(
                    usage_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "total_usage": sum(usage_stats.values())
            }