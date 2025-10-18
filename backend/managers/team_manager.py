"""
Team Management System for Google ADK
Handles multi-agent coordination and team workflows
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from loguru import logger


class TeamType(Enum):
    """Team execution types"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


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
    Team management system for coordinating multiple agents
    Supports sequential, parallel, and hierarchical team structures
    """
    
    def __init__(self, agent_manager):
        """
        Initialize team manager
        
        Args:
            agent_manager: Agent manager instance
        """
        self.agent_manager = agent_manager
        self._teams: Dict[str, TeamInfo] = {}
        self._lock = Lock()
        
        logger.info("Team manager initialized")
    
    def create_team(self,
                   name: str,
                   description: str,
                   team_type: TeamType,
                   agent_ids: List[str],
                   coordinator_id: Optional[str] = None,
                   team_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new team
        
        Args:
            name: Team name
            description: Team description
            team_type: Type of team coordination
            agent_ids: List of agent IDs in the team
            coordinator_id: Optional coordinator agent ID
            team_id: Optional custom team ID
            metadata: Optional metadata
            
        Returns:
            str: Team ID
        """
        try:
            # Validate agents exist
            for agent_id in agent_ids:
                if not self.agent_manager.get_agent_info(agent_id):
                    raise ValueError(f"Agent {agent_id} not found")
            
            # Validate coordinator if specified
            if coordinator_id and not self.agent_manager.get_agent_info(coordinator_id):
                raise ValueError(f"Coordinator agent {coordinator_id} not found")
            
            # Generate team ID
            if not team_id:
                team_id = f"team_{uuid.uuid4().hex[:8]}"
            
            # Create team info
            team_info = TeamInfo(
                team_id=team_id,
                name=name,
                description=description,
                team_type=team_type,
                agent_ids=agent_ids.copy(),
                coordinator_id=coordinator_id,
                metadata=metadata or {}
            )
            
            # Store team
            with self._lock:
                self._teams[team_id] = team_info
            
            # Create corresponding ADK team agent if needed
            if team_type in [TeamType.SEQUENTIAL, TeamType.PARALLEL]:
                self._create_adk_team_agent(team_info)
            
            logger.info(f"Created team '{name}' with ID {team_id} ({team_type.value})")
            return team_id
            
        except Exception as e:
            logger.error(f"Failed to create team '{name}': {e}")
            raise
    
    def _create_adk_team_agent(self, team_info: TeamInfo):
        """Create corresponding ADK team agent"""
        try:
            from managers.agent_manager import AgentPersona, AgentConfig
            
            # Create team persona
            persona = AgentPersona(
                name=f"Team_{team_info.name}",
                description=f"Team agent for {team_info.description}",
                personality="collaborative and coordinating",
                expertise=["team coordination", "multi-agent workflows"],
                communication_style="professional"
            )
            
            # Create team agent
            agent_type = "SequentialAgent" if team_info.team_type == TeamType.SEQUENTIAL else "ParallelAgent"
            
            team_agent_id = self.agent_manager.create_agent(
                name=f"Team_{team_info.name}",
                persona=persona,
                config=AgentConfig(),
                agent_id=f"team_agent_{team_info.team_id}",
                agent_type=agent_type,
                sub_agents=team_info.agent_ids
            )
            
            # Store team agent ID in metadata
            team_info.metadata["team_agent_id"] = team_agent_id
            
            logger.info(f"Created ADK team agent {team_agent_id} for team {team_info.team_id}")
            
        except Exception as e:
            logger.error(f"Failed to create ADK team agent: {e}")
    
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
    
    def get_team_agent(self, team_id: str):
        """Get the ADK team agent for a team"""
        team_info = self.get_team(team_id)
        if not team_info:
            return None
        
        team_agent_id = team_info.metadata.get("team_agent_id")
        if team_agent_id:
            return self.agent_manager.get_agent(team_agent_id)
        return None
    
    def update_team(self,
                   team_id: str,
                   name: Optional[str] = None,
                   description: Optional[str] = None,
                   agent_ids: Optional[List[str]] = None,
                   coordinator_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update team configuration"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                # Update fields
                if name is not None:
                    team_info.name = name
                
                if description is not None:
                    team_info.description = description
                
                if agent_ids is not None:
                    # Validate agents exist
                    for agent_id in agent_ids:
                        if not self.agent_manager.get_agent_info(agent_id):
                            raise ValueError(f"Agent {agent_id} not found")
                    team_info.agent_ids = agent_ids.copy()
                
                if coordinator_id is not None:
                    if coordinator_id and not self.agent_manager.get_agent_info(coordinator_id):
                        raise ValueError(f"Coordinator agent {coordinator_id} not found")
                    team_info.coordinator_id = coordinator_id
                
                if metadata is not None:
                    team_info.metadata.update(metadata)
                
                # Recreate ADK team agent if needed
                if agent_ids is not None and team_info.team_type in [TeamType.SEQUENTIAL, TeamType.PARALLEL]:
                    self._recreate_adk_team_agent(team_info)
            
            logger.info(f"Updated team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update team {team_id}: {e}")
            return False
    
    def _recreate_adk_team_agent(self, team_info: TeamInfo):
        """Recreate ADK team agent with updated configuration"""
        try:
            # Delete old team agent if exists
            old_team_agent_id = team_info.metadata.get("team_agent_id")
            if old_team_agent_id:
                self.agent_manager.delete_agent(old_team_agent_id)
            
            # Create new team agent
            self._create_adk_team_agent(team_info)
            
        except Exception as e:
            logger.error(f"Failed to recreate ADK team agent: {e}")
    
    def add_agent_to_team(self, team_id: str, agent_id: str) -> bool:
        """Add an agent to a team"""
        try:
            with self._lock:
                team_info = self._teams.get(team_id)
                if not team_info:
                    return False
                
                # Validate agent exists
                if not self.agent_manager.get_agent_info(agent_id):
                    raise ValueError(f"Agent {agent_id} not found")
                
                # Add agent if not already in team
                if agent_id not in team_info.agent_ids:
                    team_info.agent_ids.append(agent_id)
                    
                    # Recreate ADK team agent
                    if team_info.team_type in [TeamType.SEQUENTIAL, TeamType.PARALLEL]:
                        self._recreate_adk_team_agent(team_info)
            
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
                
                # Remove agent if in team
                if agent_id in team_info.agent_ids:
                    team_info.agent_ids.remove(agent_id)
                    
                    # Recreate ADK team agent
                    if team_info.team_type in [TeamType.SEQUENTIAL, TeamType.PARALLEL]:
                        self._recreate_adk_team_agent(team_info)
            
            logger.info(f"Removed agent {agent_id} from team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove agent from team: {e}")
            return False
    
    def list_teams(self, active_only: bool = True) -> List[TeamInfo]:
        """List all teams"""
        with self._lock:
            teams = []
            for team_info in self._teams.values():
                if active_only and not team_info.is_active:
                    continue
                teams.append(team_info)
            
            return sorted(teams, key=lambda x: x.created_at, reverse=True)
    
    def search_teams(self, query: str) -> List[TeamInfo]:
        """Search teams by name or description"""
        query_lower = query.lower()
        matches = []
        
        with self._lock:
            for team_info in self._teams.values():
                if not team_info.is_active:
                    continue
                
                if (query_lower in team_info.name.lower() or 
                    query_lower in team_info.description.lower()):
                    matches.append(team_info)
        
        return sorted(matches, key=lambda x: x.usage_count, reverse=True)
    
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
                if team_info:
                    # Delete associated team agent
                    team_agent_id = team_info.metadata.get("team_agent_id")
                    if team_agent_id:
                        self.agent_manager.delete_agent(team_agent_id)
                    
                    # Delete team
                    del self._teams[team_id]
            
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
            
            # Team type distribution
            type_stats = {}
            for team_info in self._teams.values():
                team_type = team_info.team_type.value
                type_stats[team_type] = type_stats.get(team_type, 0) + 1
            
            # Usage statistics
            usage_stats = {}
            for team_info in self._teams.values():
                usage_stats[team_info.team_id] = team_info.usage_count
            
            # Average team size
            team_sizes = [len(t.agent_ids) for t in self._teams.values()]
            avg_team_size = sum(team_sizes) / len(team_sizes) if team_sizes else 0
            
            return {
                "total_teams": total_teams,
                "active_teams": active_teams,
                "inactive_teams": total_teams - active_teams,
                "team_type_distribution": type_stats,
                "average_team_size": round(avg_team_size, 1),
                "most_used_teams": sorted(
                    usage_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "total_usage": sum(usage_stats.values())
            }
    
    def execute_team_workflow(self,
                            team_id: str,
                            input_data: Dict[str, Any],
                            user_id: str) -> Dict[str, Any]:
        """
        Execute a team workflow
        
        Args:
            team_id: Team identifier
            input_data: Input data for the workflow
            user_id: User identifier
            
        Returns:
            Dict containing workflow results
        """
        try:
            team_info = self.get_team(team_id)
            if not team_info:
                raise ValueError(f"Team {team_id} not found")
            
            logger.info(f"Executing {team_info.team_type.value} workflow for team {team_id}")
            
            if team_info.team_type == TeamType.SEQUENTIAL:
                return self._execute_sequential_workflow(team_info, input_data, user_id)
            elif team_info.team_type == TeamType.PARALLEL:
                return self._execute_parallel_workflow(team_info, input_data, user_id)
            elif team_info.team_type == TeamType.HIERARCHICAL:
                return self._execute_hierarchical_workflow(team_info, input_data, user_id)
            else:
                raise ValueError(f"Unsupported team type: {team_info.team_type}")
                
        except Exception as e:
            logger.error(f"Failed to execute team workflow: {e}")
            raise
    
    def _execute_sequential_workflow(self, team_info: TeamInfo, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute sequential workflow"""
        results = {"type": "sequential", "agent_results": []}
        current_input = input_data
        
        for i, agent_id in enumerate(team_info.agent_ids):
            try:
                agent = self.agent_manager.get_agent(agent_id)
                if not agent:
                    logger.warning(f"Agent {agent_id} not found, skipping")
                    continue
                
                # In a real implementation, you'd execute the agent here
                # For now, we'll simulate the execution
                result = {
                    "agent_id": agent_id,
                    "step": i + 1,
                    "input": current_input,
                    "output": f"Processed by {agent_id}",
                    "status": "completed"
                }
                
                results["agent_results"].append(result)
                current_input = result["output"]
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_id}: {e}")
                results["agent_results"].append({
                    "agent_id": agent_id,
                    "step": i + 1,
                    "error": str(e),
                    "status": "failed"
                })
        
        results["final_output"] = current_input
        return results
    
    def _execute_parallel_workflow(self, team_info: TeamInfo, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute parallel workflow"""
        results = {"type": "parallel", "agent_results": []}
        
        # In a real implementation, you'd execute agents in parallel
        for i, agent_id in enumerate(team_info.agent_ids):
            try:
                agent = self.agent_manager.get_agent(agent_id)
                if not agent:
                    logger.warning(f"Agent {agent_id} not found, skipping")
                    continue
                
                # Simulate parallel execution
                result = {
                    "agent_id": agent_id,
                    "input": input_data,
                    "output": f"Processed by {agent_id} in parallel",
                    "status": "completed"
                }
                
                results["agent_results"].append(result)
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_id}: {e}")
                results["agent_results"].append({
                    "agent_id": agent_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        # Combine results
        successful_results = [r["output"] for r in results["agent_results"] if r.get("status") == "completed"]
        results["combined_output"] = " | ".join(successful_results)
        
        return results
    
    def _execute_hierarchical_workflow(self, team_info: TeamInfo, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute hierarchical workflow"""
        results = {"type": "hierarchical", "coordinator_result": None, "agent_results": []}
        
        # Execute coordinator first if specified
        if team_info.coordinator_id:
            try:
                coordinator = self.agent_manager.get_agent(team_info.coordinator_id)
                if coordinator:
                    coordinator_result = {
                        "agent_id": team_info.coordinator_id,
                        "role": "coordinator",
                        "input": input_data,
                        "output": f"Coordinated by {team_info.coordinator_id}",
                        "status": "completed"
                    }
                    results["coordinator_result"] = coordinator_result
                    
            except Exception as e:
                logger.error(f"Error executing coordinator: {e}")
                results["coordinator_result"] = {
                    "agent_id": team_info.coordinator_id,
                    "role": "coordinator",
                    "error": str(e),
                    "status": "failed"
                }
        
        # Execute other agents
        for agent_id in team_info.agent_ids:
            if agent_id == team_info.coordinator_id:
                continue  # Skip coordinator as it was already executed
                
            try:
                agent = self.agent_manager.get_agent(agent_id)
                if not agent:
                    logger.warning(f"Agent {agent_id} not found, skipping")
                    continue
                
                result = {
                    "agent_id": agent_id,
                    "input": input_data,
                    "output": f"Processed by {agent_id} under coordination",
                    "status": "completed"
                }
                
                results["agent_results"].append(result)
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_id}: {e}")
                results["agent_results"].append({
                    "agent_id": agent_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return results
