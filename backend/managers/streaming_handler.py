"""
Streaming Response Handler for Google ADK
Handles real-time streaming of agent responses with optimized performance
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


class StreamingEventType(Enum):
    """Types of streaming events"""
    START = "start"
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"


@dataclass
class StreamingEvent:
    """Streaming event data structure"""
    type: StreamingEventType
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass
class StreamingSession:
    """Active streaming session"""
    session_id: str
    agent_id: str
    user_id: str
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    total_tokens: int = 0
    events_sent: int = 0
    buffer: List[str] = field(default_factory=list)


class StreamingHandler:
    """
    Handles streaming responses from agents with optimized performance
    Provides smooth 60fps rendering and batched content updates
    """
    
    def __init__(self, 
                 update_interval_ms: int = 16,  # 60fps
                 batch_size: int = 3,
                 agent_manager=None):
        """
        Initialize streaming handler
        
        Args:
            update_interval_ms: Update interval in milliseconds (default: 16ms for 60fps)
            batch_size: Number of content chunks to batch before sending (default: 3)
            agent_manager: Agent manager instance for team coordination
        """
        self.update_interval = update_interval_ms / 1000  # Convert to seconds
        self.batch_size = batch_size
        self.agent_manager = agent_manager
        self.buffer_timeout = 0.1
        
        # Session management
        self._active_sessions: Dict[str, StreamingSession] = {}
        self._event_callbacks: Dict[str, List[Callable]] = {}
        
        # Content buffering for smooth streaming
        self._content_buffers: Dict[str, List[str]] = {}
        self._last_flush_time: Dict[str, float] = {}
        
        logger.info(f"Streaming handler initialized (interval: {update_interval_ms}ms, batch: {batch_size})")

    async def start_streaming_session(self, session_id: str, agent_id: str, user_id: str, 
                                     agent, message: str) -> AsyncGenerator[StreamingEvent, None]:
        """
        Start a streaming session with an agent using proper ADK streaming
        
        Args:
            session_id: Session identifier
            agent_id: Agent identifier
            user_id: User identifier
            agent: ADK Agent instance
            message: User message string
            
        Yields:
            StreamingEvent: Stream of events
        """
        start_time = time.time()
        
        try:
            # Create streaming session
            streaming_session = StreamingSession(
                session_id=session_id,
                agent_id=agent_id,
                user_id=user_id
            )
            
            self._active_sessions[session_id] = streaming_session
            
            # Send start event
            yield StreamingEvent(
                type=StreamingEventType.START,
                session_id=session_id,
                agent_id=agent_id,
                metadata={
                    "user_id": user_id,
                    "started_at": streaming_session.started_at.isoformat(),
                    "streaming_mode": "ADK_SSE"
                }
            )
            
            # Create session service and runner with proper streaming config
            session_service = InMemorySessionService()
            runner = Runner(
                app_name="adk_streaming",
                agent=agent,
                session_service=session_service
            )
            
            # Create session
            session = await session_service.create_session(
                app_name="adk_streaming",
                user_id=user_id
            )
            
            # Configure streaming
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)
            
            logger.info(f"Starting ADK streaming for session {session_id}")
            
            # Run with proper ADK streaming
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=Content(role="user", parts=[Part(text=message)]),
                run_config=run_config
            ):
                streaming_session.last_activity = datetime.now()
                
                # Handle ADK streaming events
                event_processed = False
                
                # Handle sub-agent start events
                if hasattr(event, 'event_type') and event.event_type == 'sub_agent_start':
                    yield StreamingEvent(
                        type=StreamingEventType.START,
                        content=f"🚀 Starting sub-agent: {getattr(event, 'agent_name', 'unknown')}",
                        session_id=session_id,
                        agent_id=agent_id,
                        metadata={
                            "sub_agent_name": getattr(event, 'agent_name', 'unknown'),
                            "is_sub_agent_event": True,
                            "event_type": "sub_agent_start"
                        }
                    )
                
                # Handle sub-agent completion events
                if hasattr(event, 'event_type') and event.event_type == 'sub_agent_complete':
                    yield StreamingEvent(
                        type=StreamingEventType.COMPLETE,
                        content=f"🏁 Completed sub-agent: {getattr(event, 'agent_name', 'unknown')}",
                        session_id=session_id,
                        agent_id=agent_id,
                        metadata={
                            "sub_agent_name": getattr(event, 'agent_name', 'unknown'),
                            "is_sub_agent_event": True,
                            "event_type": "sub_agent_complete"
                        }
                    )
                
                # Handle tool calls
                if hasattr(event, 'tool_calls') and event.tool_calls:
                    for tool_call in event.tool_calls:
                        sub_agent_info = {}
                        if hasattr(event, 'agent_name') and event.agent_name:
                            sub_agent_info = {
                                "sub_agent_name": event.agent_name,
                                "is_sub_agent_tool": True
                            }
                        
                        yield StreamingEvent(
                            type=StreamingEventType.TOOL_CALL,
                            content=f"🔧 Calling tool: {getattr(tool_call, 'name', str(tool_call))}",
                            session_id=session_id,
                            agent_id=agent_id,
                            metadata={
                                "tool_name": getattr(tool_call, 'name', str(tool_call)),
                                **sub_agent_info
                            }
                        )
                
                # Handle tool responses
                if hasattr(event, 'tool_responses') and event.tool_responses:
                    for tool_response in event.tool_responses:
                        sub_agent_info = {}
                        if hasattr(event, 'agent_name') and event.agent_name:
                            sub_agent_info = {
                                "sub_agent_name": event.agent_name,
                                "is_sub_agent_tool": True
                            }
                        
                        yield StreamingEvent(
                            type=StreamingEventType.TOOL_RESPONSE,
                            content=f"✅ Tool completed: {getattr(tool_response, 'name', 'tool')}",
                            session_id=session_id,
                            agent_id=agent_id,
                            metadata={
                                "tool_name": getattr(tool_response, 'name', 'tool'),
                                **sub_agent_info
                            }
                        )
                
                # Handle thinking
                if hasattr(event, 'thinking') and event.thinking:
                    yield StreamingEvent(
                        type=StreamingEventType.THINKING,
                        content=event.thinking,
                        session_id=session_id,
                        agent_id=agent_id
                    )
                
                # Process content parts
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and not event_processed:
                    has_content = False
                    
                    for part in event.content.parts:
                        # Check for function calls first
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_call_event = StreamingEvent(
                                type=StreamingEventType.TOOL_CALL,
                                content=f"🔧 Calling tool: {part.function_call.name}",
                                session_id=session_id,
                                agent_id=agent_id,
                                metadata={
                                    "tool_name": part.function_call.name,
                                    "tool_args": dict(part.function_call.args) if part.function_call.args else {},
                                    "call_id": getattr(part.function_call, 'id', 'unknown')
                                }
                            )
                            yield tool_call_event
                        
                        # Check for function responses
                        elif hasattr(part, 'function_response') and part.function_response:
                            tool_response_event = StreamingEvent(
                                type=StreamingEventType.TOOL_RESPONSE,
                                content=f"✅ Tool '{part.function_response.name}' completed",
                                session_id=session_id,
                                agent_id=agent_id,
                                metadata={
                                    "tool_name": part.function_response.name,
                                    "response_id": getattr(part.function_response, 'id', 'unknown')
                                }
                            )
                            yield tool_response_event
                        
                        # Handle text content
                        elif part.text and part.text.strip():
                            streaming_session.events_sent += 1
                            has_content = True
                            
                            # Check if this is from a sub-agent
                            sub_agent_info = {}
                            if hasattr(event, 'agent_name') and event.agent_name:
                                sub_agent_info = {
                                    "sub_agent_name": event.agent_name,
                                    "is_sub_agent": True
                                }
                            elif hasattr(event, 'source') and event.source:
                                sub_agent_info = {
                                    "sub_agent_name": event.source,
                                    "is_sub_agent": True
                                }
                            
                            yield StreamingEvent(
                                type=StreamingEventType.CONTENT,
                                content=part.text,
                                session_id=session_id,
                                agent_id=agent_id,
                                metadata={
                                    "event_count": streaming_session.events_sent,
                                    "chunk_size": len(part.text),
                                    "is_streaming": True,
                                    **sub_agent_info
                                }
                            )
                    
                    if has_content:
                        event_processed = True
            
            # Send completion event
            completion_event = StreamingEvent(
                type=StreamingEventType.COMPLETE,
                content="",
                metadata={
                    "total_events": streaming_session.events_sent,
                    "duration_seconds": time.time() - start_time,
                    "completed_at": datetime.now().isoformat()
                }
            )
            
            yield completion_event
            
        except Exception as e:
            logger.error(f"Error processing agent events: {e}")
            error_event = StreamingEvent(
                type=StreamingEventType.ERROR,
                content=f"Streaming error: {str(e)}",
                metadata={"error_type": "processing_error"}
            )
            yield error_event
        
        finally:
            # Cleanup session
            self._cleanup_session(session_id)

    async def stream_to_sse(self,
                          session_id: str,
                          agent_id: str,
                          user_id: str,
                          agent,
                          message: str) -> AsyncGenerator[str, None]:
        """Stream responses in Server-Sent Events format"""
        async for event in self.start_streaming_session(
            session_id, agent_id, user_id, agent, message
        ):
            # Format as SSE
            sse_data = {
                "type": event.type.value,
                "content": event.content,
                "metadata": event.metadata,
                "timestamp": event.timestamp
            }
            
            yield f"data: {json.dumps(sse_data)}\n\n"
        
        # Send final SSE close
        yield "data: [DONE]\n\n"

    async def stream_to_websocket(self,
                                websocket,
                                session_id: str,
                                agent_id: str,
                                user_id: str,
                                agent,
                                message: str):
        """Stream responses to WebSocket connection"""
        try:
            async for event in self.start_streaming_session(
                session_id, agent_id, user_id, agent, message
            ):
                # Send WebSocket message
                ws_data = {
                    "type": event.type.value,
                    "content": event.content,
                    "metadata": event.metadata,
                    "timestamp": event.timestamp,
                    "session_id": session_id,
                    "agent_id": agent_id
                }
                
                await websocket.send_text(json.dumps(ws_data))
                
                # Small delay for smooth streaming
                await asyncio.sleep(0.001)
        
        except Exception as e:
            logger.error(f"WebSocket streaming error: {e}")
            # Send error to client
            error_data = {
                "type": "error",
                "content": str(e),
                "metadata": {"error_type": type(e).__name__},
                "timestamp": time.time()
            }
            try:
                await websocket.send_text(json.dumps(error_data))
            except:
                pass  # Connection might be closed

    def register_event_callback(self, 
                              event_type: StreamingEventType,
                              callback: Callable[[StreamingEvent], None]):
        """Register callback for streaming events"""
        event_key = event_type.value
        if event_key not in self._event_callbacks:
            self._event_callbacks[event_key] = []
        
        self._event_callbacks[event_key].append(callback)
        logger.debug(f"Registered callback for {event_type.value} events")

    def get_active_sessions(self) -> List[StreamingSession]:
        """Get list of active streaming sessions"""
        return [
            session for session in self._active_sessions.values()
            if session.is_active
        ]

    def get_session_info(self, session_id: str) -> Optional[StreamingSession]:
        """Get streaming session information"""
        return self._active_sessions.get(session_id)

    def stop_session(self, session_id: str) -> bool:
        """Stop an active streaming session"""
        session = self._active_sessions.get(session_id)
        if session:
            session.is_active = False
            self._cleanup_session(session_id)
            logger.info(f"Stopped streaming session {session_id}")
            return True
        return False

    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        active_sessions = self.get_active_sessions()
        
        total_events = sum(session.events_sent for session in active_sessions)
        total_tokens = sum(session.total_tokens for session in active_sessions)
        
        return {
            "active_sessions": len(active_sessions),
            "total_sessions": len(self._active_sessions),
            "total_events_sent": total_events,
            "total_tokens_processed": total_tokens,
            "update_interval_ms": self.update_interval * 1000,
            "batch_size": self.batch_size,
            "buffer_timeout_ms": self.buffer_timeout * 1000
        }

    def _cleanup_session(self, session_id: str):
        """Cleanup streaming session resources"""
        try:
            if session_id in self._active_sessions:
                self._active_sessions[session_id].is_active = False
            
            # Clean up buffers
            self._content_buffers.pop(session_id, None)
            self._last_flush_time.pop(session_id, None)
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

    async def _trigger_callbacks(self, event: StreamingEvent):
        """Trigger registered callbacks for an event"""
        try:
            callbacks = self._event_callbacks.get(event.type.value, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
        except Exception as e:
            logger.error(f"Error triggering callbacks: {e}")

    def configure_streaming(self,
                          update_interval_ms: Optional[int] = None,
                          batch_size: Optional[int] = None,
                          buffer_timeout_ms: Optional[int] = None):
        """Update streaming configuration"""
        if update_interval_ms is not None:
            self.update_interval = update_interval_ms / 1000.0
        
        if batch_size is not None:
            self.batch_size = batch_size
        
        if buffer_timeout_ms is not None:
            self.buffer_timeout = buffer_timeout_ms / 1000.0
        
        logger.info(f"Updated streaming config: interval={self.update_interval*1000}ms, batch={self.batch_size}")

    async def cleanup_expired_sessions(self, max_age_minutes: int = 30):
        """Cleanup expired streaming sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in self._active_sessions.items():
                age_minutes = (current_time - session.last_activity).total_seconds() / 60
                if age_minutes > max_age_minutes:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self.stop_session(session_id)
                del self._active_sessions[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired streaming sessions")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")

    async def shutdown(self):
        """Shutdown streaming handler"""
        try:
            # Stop all active sessions
            for session_id in list(self._active_sessions.keys()):
                self.stop_session(session_id)
            
            # Clear all data
            self._active_sessions.clear()
            self._event_callbacks.clear()
            self._content_buffers.clear()
            self._last_flush_time.clear()
            
            logger.info("Streaming handler shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during streaming handler shutdown: {e}")
