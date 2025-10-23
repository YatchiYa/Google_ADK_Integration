"""
Conversations API Router
Handles conversation management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.conversation_manager import ConversationManager, MessageRole
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_conversation_manager() -> ConversationManager:
    """Dependency to get conversation manager"""
    from main import managers
    return managers["conversation_manager"]


@router.post("/start", response_model=BaseResponse)
async def start_conversation(
    request: StartConversationRequest,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Start a new conversation"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can start conversation for this user_id
        if request.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Can only start conversations for yourself")
        
        session_id = conversation_manager.start_conversation(
            user_id=request.user_id,
            agent_id=request.agent_id,
            initial_message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        
        return BaseResponse(
            success=True,
            message=f"Conversation started with session ID: {session_id}"
        )
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get conversation by session ID"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if user can access this conversation
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert messages to response models
        messages = []
        for msg in conversation.messages:
            message_model = MessageModel(
                role=MessageRole(msg.role.value),
                content=msg.content,
                metadata=msg.metadata,
                timestamp=msg.timestamp
            )
            messages.append(message_model)
        
        return ConversationResponse(
            session_id=conversation.session_id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            messages=messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            is_active=conversation.is_active,
            metadata=conversation.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get conversation message history"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        messages = conversation_manager.get_conversation_history(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to response models
        message_responses = []
        for msg in messages:
            message_model = MessageModel(
                role=MessageRole(msg.role.value),
                content=msg.content,
                metadata=msg.metadata,
                timestamp=msg.timestamp
            )
            message_responses.append(message_model)
        
        return {
            "success": True,
            "message": f"Retrieved {len(message_responses)} messages",
            "session_id": session_id,
            "messages": message_responses,
            "total": len(conversation.messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def list_user_conversations(
    user_id: str,
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    active_only: bool = Query(True, description="Only return active conversations"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """List conversations for a user"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can access conversations for this user_id
        if user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Can only access your own conversations")
        
        conversations = conversation_manager.list_conversations(
            user_id=user_id,
            agent_id=agent_id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        
        # Convert to response models
        conversation_responses = []
        for conv in conversations:
            # Convert messages
            messages = []
            for msg in conv.messages[-5:]:  # Last 5 messages for preview
                message_model = MessageModel(
                    role=MessageRole(msg.role.value),
                    content=msg.content,
                    metadata=msg.metadata,
                    timestamp=msg.timestamp
                )
                messages.append(message_model)
            
            conv_response = ConversationResponse(
                session_id=conv.session_id,
                user_id=conv.user_id,
                agent_id=conv.agent_id,
                messages=messages,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active,
                metadata=conv.metadata
            )
            conversation_responses.append(conv_response)
        
        return {
            "success": True,
            "message": f"Retrieved {len(conversation_responses)} conversations",
            "conversations": conversation_responses,
            "total": len(conversation_responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/{agent_id}")
async def get_agent_conversations(
    agent_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for a specific agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get conversations from database
        if conversation_manager.db_service:
            db_conversations = conversation_manager.db_service.get_agent_conversations(
                agent_id, 
                limit=limit
            )
            
            conversations = []
            for db_conv in db_conversations:
                # Load messages
                db_messages = conversation_manager.db_service.get_conversation_messages(
                    db_conv.conversation_id,
                    limit=10  # Last 10 messages for preview
                )
                
                messages = []
                for db_msg in db_messages:
                    message_model = MessageModel(
                        role=MessageRole(db_msg.role),
                        content=db_msg.content or "",
                        metadata=db_msg.message_metadata or {},
                        timestamp=db_msg.created_at
                    )
                    messages.append(message_model)
                
                conv_response = ConversationResponse(
                    session_id=db_conv.conversation_id,
                    user_id="default_user",
                    agent_id=db_conv.agent_id,
                    messages=messages,
                    created_at=db_conv.created_at,
                    updated_at=db_conv.updated_at,
                    is_active=db_conv.status == "active",
                    metadata=db_conv.conversation_metadata or {}
                )
                conversations.append(conv_response)
            
            return {
                "success": True,
                "conversations": conversations,
                "total": len(conversations)
            }
        
        return {
            "success": True,
            "conversations": [],
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting agent conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}")
async def search_conversations(
    query: str,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Search conversations by content"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # If user_id not specified, use current user
        if not user_id:
            user_id = current_user["user_id"]
        
        # Verify user can search conversations for this user_id
        if user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Can only search your own conversations")
        
        conversations = conversation_manager.search_conversations(
            user_id=user_id,
            query=query,
            agent_id=agent_id,
            limit=limit
        )
        
        # Convert to response models
        conversation_responses = []
        for conv in conversations:
            # Convert messages (last 3 for preview)
            messages = []
            for msg in conv.messages[-3:]:
                message_model = MessageModel(
                    role=MessageRole(msg.role.value),
                    content=msg.content,
                    metadata=msg.metadata,
                    timestamp=msg.timestamp
                )
                messages.append(message_model)
            
            conv_response = ConversationResponse(
                session_id=conv.session_id,
                user_id=conv.user_id,
                agent_id=conv.agent_id,
                messages=messages,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active,
                metadata=conv.metadata
            )
            conversation_responses.append(conv_response)
        
        return {
            "success": True,
            "message": f"Found {len(conversation_responses)} conversations matching '{query}'",
            "conversations": conversation_responses,
            "total": len(conversation_responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/metadata", response_model=BaseResponse)
async def update_conversation_metadata(
    session_id: str,
    metadata: dict,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Update conversation metadata"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = conversation_manager.update_conversation_metadata(session_id, metadata)
        if success:
            return BaseResponse(
                success=True,
                message=f"Conversation {session_id} metadata updated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to update conversation metadata")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/end", response_model=BaseResponse)
async def end_conversation(
    session_id: str,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """End a conversation"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = conversation_manager.end_conversation(session_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Conversation {session_id} ended successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", response_model=BaseResponse)
async def delete_conversation(
    session_id: str,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = conversation_manager.delete_conversation(session_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Conversation {session_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_conversation_stats(
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get conversation statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = conversation_manager.get_conversation_stats()
        
        # Filter user stats if not admin
        conversations_by_user = stats.get("conversations_by_user", {})
        if not require_permission(current_user, "admin:conversations"):
            # Only show current user's stats
            user_id = current_user["user_id"]
            conversations_by_user = {user_id: conversations_by_user.get(user_id, 0)}
        
        filtered_stats = {
            **stats,
            "conversations_by_user": conversations_by_user
        }
        
        return {
            "success": True,
            "message": "Conversation statistics retrieved",
            "stats": filtered_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/export")
async def export_conversation(
    session_id: str,
    format: str = Query("json", description="Export format (json)"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Export conversation data"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        export_data = conversation_manager.export_conversation(session_id)
        if not export_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "message": f"Conversation {session_id} exported successfully",
            "data": export_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=BaseResponse)
async def import_conversation(
    conversation_data: dict,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Import conversation data"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can import conversation for this user_id
        if conversation_data.get("user_id") != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Can only import conversations for yourself")
        
        session_id = conversation_manager.import_conversation(conversation_data)
        if session_id:
            return BaseResponse(
                success=True,
                message=f"Conversation imported successfully with session ID: {session_id}"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to import conversation")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing conversation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cleanup", response_model=BaseResponse)
async def cleanup_old_conversations(
    days: int = Query(30, ge=1, le=365, description="Delete conversations older than this many days"),
    keep_active: bool = Query(True, description="Keep active conversations"),
    user_id: Optional[str] = Query(None, description="Cleanup for specific user (admin only)"),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Clean up old conversations"""
    try:
        # Check permissions
        if user_id and user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Admin privileges required for user-specific cleanup")
        elif not require_permission(current_user, "conversations:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        deleted_count = conversation_manager.cleanup_old_conversations(
            days=days,
            keep_active=keep_active
        )
        
        return BaseResponse(
            success=True,
            message=f"Cleaned up {deleted_count} old conversations"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
