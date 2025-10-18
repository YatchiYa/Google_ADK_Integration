"""
Streaming API Router
Handles streaming conversation endpoints
"""

import json
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from loguru import logger

from managers.conversation_manager import ConversationManager
from managers.streaming_handler import StreamingHandler
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_conversation_manager() -> ConversationManager:
    """Dependency to get conversation manager"""
    from main import managers
    return managers["conversation_manager"]


def get_streaming_handler() -> StreamingHandler:
    """Dependency to get streaming handler"""
    from main import managers
    return managers["streaming_handler"]


@router.post("/send")
async def send_message_streaming(
    session_id: str,
    request: SendMessageRequest,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Send a message and get streaming response"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        async def generate_response():
            """Generate streaming response"""
            try:
                async for response_chunk in conversation_manager.send_message(
                    session_id=session_id,
                    message=request.message,
                    metadata=request.metadata
                ):
                    yield f"data: {json.dumps(response_chunk)}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                error_response = {
                    "type": "error",
                    "content": str(e),
                    "metadata": {"error_type": type(e).__name__},
                    "timestamp": datetime.now().timestamp()
                }
                yield f"data: {json.dumps(error_response)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_streaming_conversation(
    request: StartStreamingRequest,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Start a new streaming conversation"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Verify user can start conversation for this user_id
        if request.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:conversations"):
                raise HTTPException(status_code=403, detail="Can only start conversations for yourself")
        
        # Start conversation
        session_id = conversation_manager.start_conversation(
            user_id=request.user_id,
            agent_id=request.agent_id,
            initial_message=request.message,
            session_id=request.session_id
        )
        
        # Get agent for streaming
        from main import managers
        agent_manager = managers["agent_manager"]
        agent = agent_manager.get_agent(request.agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        async def generate_response():
            """Generate streaming response"""
            try:
                async for event in streaming_handler.stream_to_sse(
                    session_id=session_id,
                    agent_id=request.agent_id,
                    user_id=request.user_id,
                    agent=agent,
                    message=request.message
                ):
                    yield event
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                error_response = {
                    "type": "error",
                    "content": str(e),
                    "metadata": {"error_type": type(e).__name__},
                    "timestamp": datetime.now().timestamp()
                }
                yield f"data: {json.dumps(error_response)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting streaming conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_conversation(
    websocket: WebSocket,
    session_id: str,
    api_key: Optional[str] = None
):
    """WebSocket endpoint for real-time conversation"""
    await websocket.accept()
    
    try:
        # Authenticate user
        from main import managers
        auth_manager = managers["auth_manager"]
        
        if api_key:
            api_key_info = auth_manager.verify_api_key(api_key)
            if not api_key_info:
                await websocket.close(code=1008, reason="Invalid API key")
                return
            user_info = {
                "user_id": api_key_info["user_id"],
                "username": api_key_info["username"],
                "auth_method": "api_key",
                "permissions": api_key_info["permissions"],
                "api_key_info": api_key_info
            }
        else:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        # Check permissions
        if not require_permission(user_info, "conversations:create"):
            await websocket.close(code=1008, reason="Insufficient permissions")
            return
        
        # Get managers
        conversation_manager = managers["conversation_manager"]
        streaming_handler = managers["streaming_handler"]
        agent_manager = managers["agent_manager"]
        
        # Check if conversation exists and user has access
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            await websocket.close(code=1008, reason="Conversation not found")
            return
        
        if conversation.user_id != user_info["user_id"]:
            if not require_permission(user_info, "admin:conversations"):
                await websocket.close(code=1008, reason="Access denied")
                return
        
        # Get agent
        agent = agent_manager.get_agent(conversation.agent_id)
        if not agent:
            await websocket.close(code=1008, reason="Agent not found")
            return
        
        logger.info(f"WebSocket connection established for session {session_id}")
        
        # Handle WebSocket messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "message":
                    message = message_data.get("content", "")
                    metadata = message_data.get("metadata", {})
                    
                    # Add user message to conversation
                    conversation_manager.add_message(
                        session_id=session_id,
                        role=MessageRole.USER,
                        content=message,
                        metadata=metadata
                    )
                    
                    # Stream agent response
                    await streaming_handler.stream_to_websocket(
                        websocket=websocket,
                        session_id=session_id,
                        agent_id=conversation.agent_id,
                        user_id=conversation.user_id,
                        agent=agent,
                        message=message
                    )
                
                elif message_data.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().timestamp()
                    }))
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "Invalid JSON format",
                    "timestamp": datetime.now().timestamp()
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": str(e),
                    "timestamp": datetime.now().timestamp()
                }))
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")


@router.get("/sessions/active")
async def get_active_streaming_sessions(
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Get active streaming sessions"""
    try:
        # Check permissions (admin only)
        if not require_permission(current_user, "admin:streaming"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        sessions = streaming_handler.get_active_sessions()
        
        session_data = []
        for session in sessions:
            session_info = {
                "session_id": session.session_id,
                "agent_id": session.agent_id,
                "user_id": session.user_id,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "events_sent": session.events_sent,
                "total_tokens": session.total_tokens
            }
            session_data.append(session_info)
        
        return {
            "success": True,
            "message": f"Retrieved {len(session_data)} active streaming sessions",
            "sessions": session_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/stop", response_model=BaseResponse)
async def stop_streaming_session(
    session_id: str,
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Stop a streaming session"""
    try:
        # Check permissions
        session_info = streaming_handler.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Streaming session not found")
        
        # Check if user can stop this session
        if session_info.user_id != current_user["user_id"]:
            if not require_permission(current_user, "admin:streaming"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        success = streaming_handler.stop_session(session_id)
        if success:
            return BaseResponse(
                success=True,
                message=f"Streaming session {session_id} stopped successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Streaming session not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping streaming session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=StreamingStatsResponse)
async def get_streaming_stats(
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Get streaming statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "streaming:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = streaming_handler.get_streaming_stats()
        
        return StreamingStatsResponse(
            active_sessions=stats["active_sessions"],
            total_sessions=stats["total_sessions"],
            total_events_sent=stats["total_events_sent"],
            total_tokens_processed=stats["total_tokens_processed"],
            update_interval_ms=stats["update_interval_ms"],
            batch_size=stats["batch_size"],
            buffer_timeout_ms=stats["buffer_timeout_ms"]
        )
        
    except Exception as e:
        logger.error(f"Error getting streaming stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/update", response_model=BaseResponse)
async def update_streaming_config(
    update_interval_ms: Optional[int] = None,
    batch_size: Optional[int] = None,
    buffer_timeout_ms: Optional[int] = None,
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Update streaming configuration"""
    try:
        # Check permissions (admin only)
        if not require_permission(current_user, "admin:streaming"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        streaming_handler.configure_streaming(
            update_interval_ms=update_interval_ms,
            batch_size=batch_size,
            buffer_timeout_ms=buffer_timeout_ms
        )
        
        return BaseResponse(
            success=True,
            message="Streaming configuration updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating streaming config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=BaseResponse)
async def cleanup_expired_sessions(
    max_age_minutes: int = 30,
    streaming_handler: StreamingHandler = Depends(get_streaming_handler),
    current_user: dict = Depends(get_current_user)
):
    """Clean up expired streaming sessions"""
    try:
        # Check permissions (admin only)
        if not require_permission(current_user, "admin:streaming"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        await streaming_handler.cleanup_expired_sessions(max_age_minutes)
        
        return BaseResponse(
            success=True,
            message=f"Cleaned up expired streaming sessions (older than {max_age_minutes} minutes)"
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
