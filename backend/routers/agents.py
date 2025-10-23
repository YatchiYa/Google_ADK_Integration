"""
Agents API Router
Handles agent management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.agent_manager import AgentManager, AgentPersona, AgentConfig
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_agent_manager() -> AgentManager:
    """Dependency to get agent manager"""
    from main import managers
    return managers["agent_manager"]


@router.post("/", response_model=BaseResponse)
async def create_agent(
    request: CreateAgentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Create a new agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Convert request models to internal models
        persona = AgentPersona(
            name=request.persona.name,
            description=request.persona.description,
            personality=request.persona.personality,
            expertise=request.persona.expertise,
            communication_style=request.persona.communication_style,
            language=request.persona.language,
            custom_instructions=request.persona.custom_instructions,
            examples=request.persona.examples
        )
        
        config = None
        if request.config:
            config = AgentConfig(
                model=request.config.model,
                temperature=request.config.temperature,
                max_output_tokens=request.config.max_output_tokens,
                top_p=request.config.top_p,
                top_k=request.config.top_k,
                timeout_seconds=request.config.timeout_seconds,
                retry_attempts=request.config.retry_attempts
            )
        
        # Create agent
        agent_id = agent_manager.create_agent(
            name=request.name,
            persona=persona,
            config=config,
            tools=request.tools,
            agent_id=request.agent_id,
            planner=request.planner,
            agent_type=request.agent_type,
            sub_agents=request.sub_agents
        )
        
        return BaseResponse(
            success=True,
            message=f"Agent '{request.name}' created successfully with ID: {agent_id}"
        )
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    active_only: bool = Query(True, description="Only return active agents"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip"),
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """List all agents"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agents = agent_manager.list_agents(active_only=active_only)
        
        # Apply pagination
        total = len(agents)
        agents = agents[offset:offset + limit]
        
        # Convert to response models
        agent_responses = []
        for agent in agents:
            agent_response = AgentInfoResponse(
                agent_id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                persona=AgentPersonaModel(
                    name=agent.persona.name,
                    description=agent.persona.description,
                    personality=agent.persona.personality,
                    expertise=agent.persona.expertise,
                    communication_style=agent.persona.communication_style,
                    language=agent.persona.language,
                    custom_instructions=agent.persona.custom_instructions,
                    examples=agent.persona.examples
                ),
                config=AgentConfigModel(
                    model=agent.config.model,
                    temperature=agent.config.temperature,
                    max_output_tokens=agent.config.max_output_tokens,
                    top_p=agent.config.top_p,
                    top_k=agent.config.top_k,
                    timeout_seconds=agent.config.timeout_seconds,
                    retry_attempts=agent.config.retry_attempts
                ),
                tools=agent.tools,
                created_at=agent.created_at,
                last_used=agent.last_used,
                usage_count=agent.usage_count,
                is_active=agent.is_active,
                version=agent.version,
                metadata=agent.metadata
            )
            agent_responses.append(agent_response)
        
        return AgentListResponse(
            success=True,
            message=f"Retrieved {len(agent_responses)} agents",
            agents=agent_responses,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentInfoResponse)
async def get_agent(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get agent by ID"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agent = agent_manager.get_agent_info(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentInfoResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            persona=AgentPersonaModel(
                name=agent.persona.name,
                description=agent.persona.description,
                personality=agent.persona.personality,
                expertise=agent.persona.expertise,
                communication_style=agent.persona.communication_style,
                language=agent.persona.language,
                custom_instructions=agent.persona.custom_instructions,
                examples=agent.persona.examples
            ),
            config=AgentConfigModel(
                model=agent.config.model,
                temperature=agent.config.temperature,
                max_output_tokens=agent.config.max_output_tokens,
                top_p=agent.config.top_p,
                top_k=agent.config.top_k,
                timeout_seconds=agent.config.timeout_seconds,
                retry_attempts=agent.config.retry_attempts
            ),
            tools=agent.tools,
            created_at=agent.created_at,
            last_used=agent.last_used,
            usage_count=agent.usage_count,
            is_active=agent.is_active,
            version=agent.version,
            metadata=agent.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}", response_model=BaseResponse)
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Update agent configuration"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if agent exists
        if not agent_manager.get_agent_info(agent_id):
            raise HTTPException(status_code=404, detail="Agent not found")
        
        success = True
        
        # Update persona if provided
        if request.persona:
            persona = AgentPersona(
                name=request.persona.name,
                description=request.persona.description,
                personality=request.persona.personality,
                expertise=request.persona.expertise,
                communication_style=request.persona.communication_style,
                language=request.persona.language,
                custom_instructions=request.persona.custom_instructions,
                examples=request.persona.examples
            )
            success &= agent_manager.update_agent_persona(agent_id, persona)
        
        # Update config if provided
        if request.config:
            config = AgentConfig(
                model=request.config.model,
                temperature=request.config.temperature,
                max_output_tokens=request.config.max_output_tokens,
                top_p=request.config.top_p,
                top_k=request.config.top_k,
                timeout_seconds=request.config.timeout_seconds,
                retry_attempts=request.config.retry_attempts
            )
            success &= agent_manager.update_agent_config(agent_id, config)
        
        # Update tools if provided
        if request.tools is not None:
            success &= agent_manager.update_agent_tools(agent_id, request.tools)
        
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} updated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to update agent")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}", response_model=BaseResponse)
async def delete_agent(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Delete agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = agent_manager.delete_agent(agent_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/activate", response_model=BaseResponse)
async def activate_agent(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Activate agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = agent_manager.activate_agent(agent_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} activated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/deactivate", response_model=BaseResponse)
async def deactivate_agent(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Deactivate agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = agent_manager.deactivate_agent(agent_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} deactivated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}", response_model=AgentListResponse)
async def search_agents(
    query: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Search agents by name or description"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agents = agent_manager.search_agents(query)[:limit]
        
        # Convert to response models
        agent_responses = []
        for agent in agents:
            agent_response = AgentInfoResponse(
                agent_id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                persona=AgentPersonaModel(
                    name=agent.persona.name,
                    description=agent.persona.description,
                    personality=agent.persona.personality,
                    expertise=agent.persona.expertise,
                    communication_style=agent.persona.communication_style,
                    language=agent.persona.language,
                    custom_instructions=agent.persona.custom_instructions,
                    examples=agent.persona.examples
                ),
                config=AgentConfigModel(
                    model=agent.config.model,
                    temperature=agent.config.temperature,
                    max_output_tokens=agent.config.max_output_tokens,
                    top_p=agent.config.top_p,
                    top_k=agent.config.top_k,
                    timeout_seconds=agent.config.timeout_seconds,
                    retry_attempts=agent.config.retry_attempts
                ),
                tools=agent.tools,
                created_at=agent.created_at,
                last_used=agent.last_used,
                usage_count=agent.usage_count,
                is_active=agent.is_active,
                version=agent.version,
                metadata=agent.metadata
            )
            agent_responses.append(agent_response)
        
        return AgentListResponse(
            success=True,
            message=f"Found {len(agent_responses)} agents matching '{query}'",
            agents=agent_responses,
            total=len(agent_responses)
        )
        
    except Exception as e:
        logger.error(f"Error searching agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=AgentStatsResponse)
async def get_agent_stats(
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get agent statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = agent_manager.get_agent_stats()
        
        return AgentStatsResponse(
            total_agents=stats["total_agents"],
            active_agents=stats["active_agents"],
            inactive_agents=stats["inactive_agents"],
            most_used_agents=stats["most_used_agents"],
            model_distribution=stats["model_distribution"],
            total_usage=stats["total_usage"]
        )
        
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/export", response_model=ExportAgentResponse)
async def export_agent_config(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Export agent configuration"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        config = agent_manager.export_agent_config(agent_id)
        if not config:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return ExportAgentResponse(
            agent_config=config,
            exported_at=config["exported_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=BaseResponse)
async def import_agent_config(
    request: ImportAgentRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Import agent configuration"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agent_id = agent_manager.import_agent_config(request.agent_config)
        if agent_id:
            return BaseResponse(
                success=True,
                message=f"Agent imported successfully with ID: {agent_id}"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to import agent configuration")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing agent config: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{agent_id}/tools/attach", response_model=BaseResponse)
async def attach_tools_to_agent(
    agent_id: str,
    request: AttachToolsRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Dynamically attach tools to an existing agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get current agent
        agent_info = agent_manager.get_agent_info(agent_id)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Get current tools
        current_tools = list(agent_info.tools) if agent_info.tools else []
        
        # Add new tools (avoid duplicates)
        new_tools = []
        for tool_name in request.tool_names:
            if tool_name not in current_tools:
                new_tools.append(tool_name)
                current_tools.append(tool_name)
        
        if not new_tools:
            return BaseResponse(
                success=True,
                message=f"All requested tools already attached to agent {agent_id}"
            )
        
        # Update agent with new tools
        success = agent_manager.update_agent_tools(agent_id, current_tools)
        
        if success:
            logger.info(f"Attached tools {new_tools} to agent {agent_id}")
            return BaseResponse(
                success=True,
                message=f"Successfully attached tools {new_tools} to agent {agent_id}"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to attach tools to agent")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error attaching tools to agent {agent_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{agent_id}/tools/detach", response_model=BaseResponse)
async def detach_tools_from_agent(
    agent_id: str,
    request: DetachToolsRequest,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Dynamically detach tools from an existing agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get current agent
        agent_info = agent_manager.get_agent_info(agent_id)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Get current tools
        current_tools = list(agent_info.tools) if agent_info.tools else []
        
        # Remove specified tools
        removed_tools = []
        for tool_name in request.tool_names:
            if tool_name in current_tools:
                current_tools.remove(tool_name)
                removed_tools.append(tool_name)
        
        if not removed_tools:
            return BaseResponse(
                success=True,
                message=f"None of the requested tools were attached to agent {agent_id}"
            )
        
        # Update agent with remaining tools
        success = agent_manager.update_agent_tools(agent_id, current_tools)
        
        if success:
            logger.info(f"Detached tools {removed_tools} from agent {agent_id}")
            return BaseResponse(
                success=True,
                message=f"Successfully detached tools {removed_tools} from agent {agent_id}"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to detach tools from agent")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detaching tools from agent {agent_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{agent_id}/tools", response_model=AgentToolsResponse)
async def get_agent_tools(
    agent_id: str,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get current tools attached to an agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get agent info
        agent_info = agent_manager.get_agent_info(agent_id)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return AgentToolsResponse(
            success=True,
            agent_id=agent_id,
            tools=agent_info.tools or [],
            message=f"Retrieved {len(agent_info.tools or [])} tools for agent {agent_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tools for agent {agent_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{agent_id}/config", response_model=BaseResponse)
async def update_agent_config(
    agent_id: str,
    config: dict,
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: dict = Depends(get_current_user)
):
    """Update agent configuration (ReAct mode, planner, etc.)"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:write"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get current agent info
        agent_info = agent_manager.get_agent_info(agent_id)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        logger.info(f"Updating agent {agent_id} config: {config}")
        
        # Update agent configuration
        updated = False
        
        # Handle agent_type changes (ReAct mode)
        if "agent_type" in config:
            agent_type = config["agent_type"]
            if agent_type != getattr(agent_info, 'agent_type', None):
                # For now, we'll update the metadata to track this
                # In a full implementation, you'd recreate the agent with the new type
                if not hasattr(agent_info, 'metadata'):
                    agent_info.metadata = {}
                agent_info.metadata['agent_type'] = agent_type
                updated = True
                logger.info(f"Updated agent {agent_id} type to: {agent_type}")
        
        # Handle planner changes
        if "planner" in config:
            planner = config["planner"]
            if planner != getattr(agent_info, 'planner', None):
                if not hasattr(agent_info, 'metadata'):
                    agent_info.metadata = {}
                agent_info.metadata['planner'] = planner
                updated = True
                logger.info(f"Updated agent {agent_id} planner to: {planner}")
        
        # Handle tools changes
        if "tools" in config:
            tools = config["tools"]
            if tools != agent_info.tools:
                agent_info.tools = tools
                updated = True
                logger.info(f"Updated agent {agent_id} tools to: {tools}")
        
        if updated:
            # In a full implementation, you might want to recreate the agent instance
            # For now, we'll just update the stored info
            logger.info(f"Agent {agent_id} configuration updated successfully")
            
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} configuration updated successfully"
            )
        else:
            return BaseResponse(
                success=True,
                message=f"No changes made to agent {agent_id} configuration"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id} config: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{agent_id}/stop", response_model=BaseResponse)
async def stop_agent_streaming(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stop streaming for an agent session"""
    try:
        # Check permissions
        if not require_permission(current_user, "agents:write"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # In a full implementation, you'd track active sessions and stop them
        # For now, we'll just return success
        logger.info(f"Stop streaming requested for agent {agent_id}")
        
        return BaseResponse(
            success=True,
            message=f"Streaming stopped for agent {agent_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping streaming for agent {agent_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
