"""
Teams API Router
Handles team management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.team_manager import TeamManager, TeamType
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_team_manager() -> TeamManager:
    """Dependency to get team manager"""
    from main import managers
    return managers["team_manager"]


@router.post("/", response_model=BaseResponse)
async def create_team(
    request: CreateTeamRequest,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Create a new team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        team_id = team_manager.create_team(
            name=request.name,
            description=request.description,
            team_type=request.team_type,
            agent_ids=request.agent_ids,
            coordinator_id=request.coordinator_id,
            metadata=request.metadata
        )
        
        return BaseResponse(
            success=True,
            message=f"Team '{request.name}' created successfully with ID: {team_id}"
        )
        
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    active_only: bool = Query(True, description="Only return active teams"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of teams to return"),
    offset: int = Query(0, ge=0, description="Number of teams to skip"),
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """List all teams"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        teams = team_manager.list_teams(active_only=active_only)
        
        # Apply pagination
        total = len(teams)
        teams = teams[offset:offset + limit]
        
        # Convert to response models
        team_responses = []
        for team in teams:
            team_response = TeamInfoResponse(
                team_id=team.team_id,
                name=team.name,
                description=team.description,
                team_type=team.team_type,
                agent_ids=team.agent_ids,
                coordinator_id=team.coordinator_id,
                created_at=team.created_at,
                last_used=team.last_used,
                usage_count=team.usage_count,
                is_active=team.is_active,
                metadata=team.metadata
            )
            team_responses.append(team_response)
        
        return TeamListResponse(
            success=True,
            message=f"Retrieved {len(team_responses)} teams",
            teams=team_responses,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}", response_model=TeamInfoResponse)
async def get_team(
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get team by ID"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        team = team_manager.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return TeamInfoResponse(
            team_id=team.team_id,
            name=team.name,
            description=team.description,
            team_type=team.team_type,
            agent_ids=team.agent_ids,
            coordinator_id=team.coordinator_id,
            created_at=team.created_at,
            last_used=team.last_used,
            usage_count=team.usage_count,
            is_active=team.is_active,
            metadata=team.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{team_id}", response_model=BaseResponse)
async def update_team(
    team_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    agent_ids: Optional[List[str]] = None,
    coordinator_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Update team configuration"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.update_team(
            team_id=team_id,
            name=name,
            description=description,
            agent_ids=agent_ids,
            coordinator_id=coordinator_id,
            metadata=metadata
        )
        
        if success:
            return BaseResponse(
                success=True,
                message=f"Team {team_id} updated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}", response_model=BaseResponse)
async def delete_team(
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Delete team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.delete_team(team_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Team {team_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/agents/{agent_id}", response_model=BaseResponse)
async def add_agent_to_team(
    team_id: str,
    agent_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Add agent to team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.add_agent_to_team(team_id, agent_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} added to team {team_id}"
            )
        else:
            raise HTTPException(status_code=404, detail="Team or agent not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding agent to team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}/agents/{agent_id}", response_model=BaseResponse)
async def remove_agent_from_team(
    team_id: str,
    agent_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Remove agent from team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.remove_agent_from_team(team_id, agent_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Agent {agent_id} removed from team {team_id}"
            )
        else:
            raise HTTPException(status_code=404, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing agent from team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/activate", response_model=BaseResponse)
async def activate_team(
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Activate team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.activate_team(team_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Team {team_id} activated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/deactivate", response_model=BaseResponse)
async def deactivate_team(
    team_id: str,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Deactivate team"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = team_manager.deactivate_team(team_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Team {team_id} deactivated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Team not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}", response_model=TeamListResponse)
async def search_teams(
    query: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Search teams by name or description"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        teams = team_manager.search_teams(query)[:limit]
        
        # Convert to response models
        team_responses = []
        for team in teams:
            team_response = TeamInfoResponse(
                team_id=team.team_id,
                name=team.name,
                description=team.description,
                team_type=team.team_type,
                agent_ids=team.agent_ids,
                coordinator_id=team.coordinator_id,
                created_at=team.created_at,
                last_used=team.last_used,
                usage_count=team.usage_count,
                is_active=team.is_active,
                metadata=team.metadata
            )
            team_responses.append(team_response)
        
        return TeamListResponse(
            success=True,
            message=f"Found {len(team_responses)} teams matching '{query}'",
            teams=team_responses,
            total=len(team_responses)
        )
        
    except Exception as e:
        logger.error(f"Error searching teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/execute")
async def execute_team_workflow(
    team_id: str,
    input_data: dict,
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Execute team workflow"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:execute"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = team_manager.execute_team_workflow(
            team_id=team_id,
            input_data=input_data,
            user_id=current_user["user_id"]
        )
        
        return {
            "success": True,
            "message": f"Team workflow executed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing team workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_team_stats(
    team_manager: TeamManager = Depends(get_team_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get team statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = team_manager.get_team_stats()
        
        return {
            "success": True,
            "message": "Team statistics retrieved",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting team stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types/list")
async def list_team_types(
    current_user: dict = Depends(get_current_user)
):
    """List available team types"""
    try:
        # Check permissions
        if not require_permission(current_user, "teams:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        team_types = [
            {
                "type": TeamType.SEQUENTIAL.value,
                "name": "Sequential",
                "description": "Agents execute one after another, passing results forward"
            },
            {
                "type": TeamType.PARALLEL.value,
                "name": "Parallel",
                "description": "Agents execute simultaneously and results are combined"
            },
            {
                "type": TeamType.HIERARCHICAL.value,
                "name": "Hierarchical",
                "description": "Coordinator agent manages and delegates to sub-agents"
            }
        ]
        
        return {
            "success": True,
            "message": "Team types retrieved",
            "team_types": team_types
        }
        
    except Exception as e:
        logger.error(f"Error listing team types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
