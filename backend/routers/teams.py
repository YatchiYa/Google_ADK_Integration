"""
Teams API Router
Handles team management endpoints for multi-agent coordination
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.team_manager import TeamManager, TeamType
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


@router.post("/", response_model=BaseResponse)
async def create_team(
    request: CreateTeamRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new multi-agent team"""
    # Check permissions
    if not require_permission(current_user, "teams:create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        team_id = team_manager.create_team(
            name=request.name,
            description=request.description,
            team_type=request.team_type,
            agent_ids=request.agent_ids,
            metadata=request.metadata
        )
        
        return BaseResponse(
            success=True,
            message=f"Team created successfully with ID: {team_id}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    active_only: bool = Query(True, description="Only return active teams"),
    current_user: dict = Depends(get_current_user)
):
    """List all teams"""
    # Check permissions
    if not require_permission(current_user, "teams:read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        teams = team_manager.list_teams(active_only=active_only)
        
        team_responses = []
        for team in teams:
            team_responses.append(TeamInfoResponse(
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
            ))
        
        return TeamListResponse(
            success=True,
            message=f"Retrieved {len(team_responses)} teams",
            teams=team_responses,
            total=len(team_responses)
        )
        
    except Exception as e:
        logger.error(f"Failed to list teams: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{team_id}", response_model=TeamInfoResponse)
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get team information by ID"""
    # Check permissions
    if not require_permission(current_user, "teams:read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
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
        logger.error(f"Failed to get team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{team_id}", response_model=BaseResponse)
async def update_team(
    team_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    agent_ids: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update team configuration"""
    # Check permissions
    if not require_permission(current_user, "teams:update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.update_team(
            team_id=team_id,
            name=name,
            description=description,
            agent_ids=agent_ids
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Team {team_id} updated successfully"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{team_id}/agents/{agent_id}", response_model=BaseResponse)
async def add_agent_to_team(
    team_id: str,
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Add an agent to a team"""
    # Check permissions
    if not require_permission(current_user, "teams:update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.add_agent_to_team(team_id, agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Agent {agent_id} added to team {team_id}"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add agent {agent_id} to team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{team_id}/agents/{agent_id}", response_model=BaseResponse)
async def remove_agent_from_team(
    team_id: str,
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove an agent from a team"""
    # Check permissions
    if not require_permission(current_user, "teams:update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.remove_agent_from_team(team_id, agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Agent {agent_id} removed from team {team_id}"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to remove agent {agent_id} from team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{team_id}/activate", response_model=BaseResponse)
async def activate_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Activate a team"""
    # Check permissions
    if not require_permission(current_user, "teams:update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.activate_team(team_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Team {team_id} activated"
        )
        
    except Exception as e:
        logger.error(f"Failed to activate team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{team_id}/deactivate", response_model=BaseResponse)
async def deactivate_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate a team"""
    # Check permissions
    if not require_permission(current_user, "teams:update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.deactivate_team(team_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Team {team_id} deactivated"
        )
        
    except Exception as e:
        logger.error(f"Failed to deactivate team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{team_id}", response_model=BaseResponse)
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a team permanently"""
    # Check permissions
    if not require_permission(current_user, "teams:delete"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        success = team_manager.delete_team(team_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return BaseResponse(
            success=True,
            message=f"Team {team_id} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{team_id}/coordinator", response_model=dict)
async def get_team_coordinator(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get team coordinator agent ID"""
    # Check permissions
    if not require_permission(current_user, "teams:read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        coordinator_id = team_manager.get_team_coordinator(team_id)
        if not coordinator_id:
            raise HTTPException(status_code=404, detail="Team or coordinator not found")
        
        return {
            "success": True,
            "team_id": team_id,
            "coordinator_id": coordinator_id,
            "message": f"Coordinator for team {team_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get coordinator for team {team_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/overview")
async def get_team_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get team statistics"""
    # Check permissions
    if not require_permission(current_user, "teams:read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from main import team_manager
        
        stats = team_manager.get_team_stats()
        
        return {
            "success": True,
            "message": "Team statistics retrieved",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get team stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")