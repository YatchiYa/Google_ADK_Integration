"""
Memory API Router
Handles memory management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.memory_manager import MemoryManager
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_memory_manager() -> MemoryManager:
    """Dependency to get memory manager"""
    from main import managers
    return managers["memory_manager"]


@router.post("/", response_model=BaseResponse)
async def create_memory(
    request: CreateMemoryRequest,
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Create a new memory entry"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can create memory for this user_id
        if request.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Can only create memories for yourself")
        
        entry_id = memory_manager.create_memory(
            user_id=request.user_id,
            content=request.entry.content,
            session_id=request.session_id,
            agent_id=request.agent_id,
            metadata=request.entry.metadata,
            tags=request.entry.tags,
            importance=request.entry.importance
        )
        
        return BaseResponse(
            success=True,
            message=f"Memory entry created with ID: {entry_id}"
        )
        
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entry_id}", response_model=MemoryEntryResponse)
async def get_memory(
    entry_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get memory entry by ID"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        memory = memory_manager.get_memory(entry_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory entry not found")
        
        # Check if user can access this memory
        if memory.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        return MemoryEntryResponse(
            entry_id=memory.entry_id,
            user_id=memory.user_id,
            session_id=memory.session_id,
            agent_id=memory.agent_id,
            content=memory.content,
            metadata=memory.metadata,
            tags=memory.tags,
            importance=memory.importance,
            relevance_score=memory.relevance_score,
            created_at=memory.created_at,
            updated_at=memory.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemoryListResponse)
async def search_memories(
    request: SearchMemoryRequest,
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Search memory entries"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can search memories for this user_id
        if request.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Can only search your own memories")
        
        memories = memory_manager.search_memories(
            user_id=request.user_id,
            query=request.query,
            limit=request.limit,
            min_relevance=request.min_relevance,
            tags=request.tags,
            session_id=request.session_id,
            agent_id=request.agent_id
        )
        
        # Convert to response models
        memory_responses = []
        for memory in memories:
            memory_response = MemoryEntryResponse(
                entry_id=memory.entry_id,
                user_id=memory.user_id,
                session_id=memory.session_id,
                agent_id=memory.agent_id,
                content=memory.content,
                metadata=memory.metadata,
                tags=memory.tags,
                importance=memory.importance,
                relevance_score=memory.relevance_score,
                created_at=memory.created_at,
                updated_at=memory.updated_at
            )
            memory_responses.append(memory_response)
        
        return MemoryListResponse(
            success=True,
            message=f"Found {len(memory_responses)} memories matching '{request.query}'",
            entries=memory_responses,
            total=len(memory_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=MemoryListResponse)
async def list_user_memories(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of memories to return"),
    offset: int = Query(0, ge=0, description="Number of memories to skip"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """List memories for a user"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can access memories for this user_id
        if user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Can only access your own memories")
        
        memories = memory_manager.list_memories(
            user_id=user_id,
            limit=limit,
            offset=offset,
            session_id=session_id,
            agent_id=agent_id
        )
        
        # Convert to response models
        memory_responses = []
        for memory in memories:
            memory_response = MemoryEntryResponse(
                entry_id=memory.entry_id,
                user_id=memory.user_id,
                session_id=memory.session_id,
                agent_id=memory.agent_id,
                content=memory.content,
                metadata=memory.metadata,
                tags=memory.tags,
                importance=memory.importance,
                created_at=memory.created_at,
                updated_at=memory.updated_at
            )
            memory_responses.append(memory_response)
        
        return MemoryListResponse(
            success=True,
            message=f"Retrieved {len(memory_responses)} memories for user {user_id}",
            entries=memory_responses,
            total=len(memory_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=BaseResponse)
async def update_memory(
    entry_id: str,
    content: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[List[str]] = None,
    importance: Optional[float] = None,
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Update memory entry"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if memory exists and user has access
        memory = memory_manager.get_memory(entry_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory entry not found")
        
        if memory.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = memory_manager.update_memory(
            entry_id=entry_id,
            content=content,
            metadata=metadata,
            tags=tags,
            importance=importance
        )
        
        if success:
            return BaseResponse(
                success=True,
                message=f"Memory entry {entry_id} updated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to update memory entry")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}", response_model=BaseResponse)
async def delete_memory(
    entry_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Delete memory entry"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if memory exists and user has access
        memory = memory_manager.get_memory(entry_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory entry not found")
        
        if memory.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = memory_manager.delete_memory(entry_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Memory entry {entry_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Memory entry not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=MemoryStatsResponse)
async def get_memory_stats(
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get memory statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "memory:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = memory_manager.get_memory_stats()
        
        # Filter user stats if not admin
        entries_by_user = stats.get("entries_by_user", {})
        if not require_permission(current_user, "admin:memory"):
            # Only show current user's stats
            user_id = current_user["user_id"]
            entries_by_user = {user_id: entries_by_user.get(user_id, 0)}
        
        return MemoryStatsResponse(
            total_entries=stats["total_entries"],
            entries_by_user=entries_by_user,
            entries_by_agent=stats["entries_by_agent"],
            storage_size_mb=stats["storage_size_mb"],
            average_importance=stats["average_importance"]
        )
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=BaseResponse)
async def cleanup_old_memories(
    days: int = Query(30, ge=1, le=365, description="Delete memories older than this many days"),
    keep_important: bool = Query(True, description="Keep memories with high importance"),
    user_id: Optional[str] = Query(None, description="Cleanup for specific user (admin only)"),
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Clean up old memories"""
    try:
        # Check permissions
        if user_id and user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Admin privileges required for user-specific cleanup")
        elif not require_permission(current_user, "memory:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        deleted_count = memory_manager.cleanup_old_memories(
            days=days,
            keep_important=keep_important
        )
        
        return BaseResponse(
            success=True,
            message=f"Cleaned up {deleted_count} old memory entries"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/user/{user_id}")
async def export_user_memories(
    user_id: str,
    format: str = Query("json", description="Export format (json)"),
    memory_manager: MemoryManager = Depends(get_memory_manager),
    current_user: dict = Depends(get_current_user)
):
    """Export user memories"""
    try:
        # Check permissions
        if user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:memory"):
                raise HTTPException(status_code=403, detail="Can only export your own memories")
        
        if not require_permission(current_user, "memory:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        memories = memory_manager.list_memories(user_id=user_id, limit=10000)
        
        export_data = {
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "total_entries": len(memories),
            "memories": [
                {
                    "entry_id": memory.entry_id,
                    "content": memory.content,
                    "metadata": memory.metadata,
                    "tags": memory.tags,
                    "importance": memory.importance,
                    "session_id": memory.session_id,
                    "agent_id": memory.agent_id,
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat()
                }
                for memory in memories
            ]
        }
        
        return {
            "success": True,
            "message": f"Exported {len(memories)} memories for user {user_id}",
            "data": export_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
